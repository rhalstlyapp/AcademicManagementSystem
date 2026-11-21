"""Pembuatan KRS mahasiswa dan persetujuan oleh dosen PA."""
from database import connection as db
from utils import session
from utils.permissions import DOSEN, MAHASISWA, require_role
from utils.validators import ValidationError, cek_id


def _mahasiswa_id():
    value = session.get_user().get("mahasiswa_id")
    if value is None:
        raise ValidationError("Akun belum terhubung ke profil mahasiswa.")
    return value


def _dosen_id():
    value = session.get_user().get("dosen_id")
    if value is None:
        raise ValidationError("Akun belum terhubung ke profil dosen.")
    return value


def _semester_aktif(cur=None, cek_periode=True):
    query = "SELECT semester_id, kode_semester, tahun_akademik, tgl_mulai_krs, tgl_selesai_krs "
    query += "FROM semester_akademik WHERE is_aktif = TRUE "
    if cek_periode:
        query += "AND CURDATE() BETWEEN tgl_mulai_krs AND tgl_selesai_krs "
    query += "LIMIT 1"
    if cur is not None:
        cur.execute(query)
        row = cur.fetchone()
    else:
        row = db.fetch_one(query)
    if row is None and cek_periode:
        raise ValidationError("Belum ada periode KRS yang sedang dibuka.")
    return row


def _ambil_atau_buat_draft(cur, mahasiswa_id, semester_id):
    cur.execute(
        "SELECT krs_id, status FROM krs WHERE mahasiswa_id = %s AND semester_id = %s FOR UPDATE",
        (mahasiswa_id, semester_id),
    )
    krs = cur.fetchone()
    if krs is None:
        cur.execute(
            "INSERT INTO krs (mahasiswa_id, semester_id, status) VALUES (%s, %s, 'Draft')",
            (mahasiswa_id, semester_id),
        )
        return {"krs_id": cur.lastrowid, "status": "Draft"}
    if krs["status"] == "Ditolak":
        cur.execute(
            "UPDATE krs SET status = 'Draft', tgl_pengajuan = NULL, disetujui_oleh = NULL, "
            "tgl_persetujuan = NULL, catatan_pa = NULL WHERE krs_id = %s",
            (krs["krs_id"],),
        )
        return {"krs_id": krs["krs_id"], "status": "Draft"}
    return krs


@require_role(MAHASISWA)
def ringkasan_saya():
    mahasiswa_id = _mahasiswa_id()
    semester = _semester_aktif(cek_periode=False)
    if semester is None:
        raise ValidationError("Belum ada semester aktif.")
    krs = db.fetch_one(
        "SELECT krs_id, status, tgl_pengajuan, tgl_persetujuan, catatan_pa "
        "FROM krs WHERE mahasiswa_id = %s AND semester_id = %s",
        (mahasiswa_id, semester["semester_id"]),
    )
    detail = []
    if krs:
        detail = db.fetch_all(
            "SELECT kd.krs_detail_id, kl.kelas_id, kl.nama_kelas, kl.kuota, "
            "mk.kode_mk, mk.nama_mk, mk.sks, p.nama_prodi "
            "FROM krs_detail kd JOIN kelas kl ON kl.kelas_id = kd.kelas_id "
            "JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id "
            "JOIN kurikulum ku ON ku.kurikulum_id = mk.kurikulum_id "
            "JOIN program_studi p ON p.prodi_id = ku.prodi_id "
            "WHERE kd.krs_id = %s ORDER BY mk.kode_mk, kl.nama_kelas",
            (krs["krs_id"],),
        )
    return {"semester": semester, "krs": krs, "detail": detail}


@require_role(MAHASISWA)
def kelas_tersedia():
    mahasiswa_id = _mahasiswa_id()
    semester = _semester_aktif()
    with db.db_cursor(commit=True) as cur:
        krs = _ambil_atau_buat_draft(cur, mahasiswa_id, semester["semester_id"])
        if krs["status"] != "Draft":
            return []
        cur.execute("SELECT prodi_id FROM mahasiswa WHERE mahasiswa_id = %s", (mahasiswa_id,))
        student = cur.fetchone()
        if student is None:
            raise ValidationError("Profil mahasiswa tidak ditemukan.")
        cur.execute(
            "SELECT kl.kelas_id, kl.nama_kelas, kl.kuota, mk.mk_id, mk.kode_mk, "
            "mk.nama_mk, mk.sks, p.nama_prodi, "
            "(SELECT COUNT(*) FROM krs_detail kd2 JOIN krs k2 ON k2.krs_id = kd2.krs_id "
            "WHERE kd2.kelas_id = kl.kelas_id AND k2.status IN ('Diajukan','Disetujui')) AS terdaftar "
            "FROM kelas kl JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id "
            "JOIN kurikulum ku ON ku.kurikulum_id = mk.kurikulum_id "
            "JOIN program_studi p ON p.prodi_id = ku.prodi_id "
            "WHERE kl.semester_id = %s AND p.prodi_id = %s AND kl.kuota > "
            "(SELECT COUNT(*) FROM krs_detail kd2 JOIN krs k2 ON k2.krs_id = kd2.krs_id "
            "WHERE kd2.kelas_id = kl.kelas_id AND k2.status IN ('Diajukan','Disetujui')) "
            "AND NOT EXISTS (SELECT 1 FROM krs_detail mine "
            "JOIN kelas mine_class ON mine_class.kelas_id = mine.kelas_id "
            "WHERE mine.krs_id = %s AND (mine.kelas_id = kl.kelas_id OR mine_class.mk_id = mk.mk_id)) "
            "ORDER BY mk.semester_paket, mk.kode_mk, kl.nama_kelas",
            (semester["semester_id"], student["prodi_id"], krs["krs_id"]),
        )
        return cur.fetchall()


@require_role(MAHASISWA)
def ambil_kelas(kelas_id):
    mahasiswa_id = _mahasiswa_id()
    kelas_id = cek_id(kelas_id, "Kelas")
    with db.db_cursor(commit=True) as cur:
        semester = _semester_aktif(cur)
        krs = _ambil_atau_buat_draft(cur, mahasiswa_id, semester["semester_id"])
        if krs["status"] != "Draft":
            raise ValidationError("KRS yang sudah diajukan tidak dapat diubah.")
        cur.execute("SELECT prodi_id FROM mahasiswa WHERE mahasiswa_id = %s", (mahasiswa_id,))
        student = cur.fetchone()
        cur.execute(
            "SELECT kl.kelas_id, kl.mk_id, kl.kuota, p.prodi_id "
            "FROM kelas kl JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id "
            "JOIN kurikulum ku ON ku.kurikulum_id = mk.kurikulum_id "
            "JOIN program_studi p ON p.prodi_id = ku.prodi_id "
            "WHERE kl.kelas_id = %s AND kl.semester_id = %s FOR UPDATE",
            (kelas_id, semester["semester_id"]),
        )
        kelas = cur.fetchone()
        if kelas is None or kelas["prodi_id"] != student["prodi_id"]:
            raise ValidationError("Kelas tidak tersedia untuk program studi mahasiswa.")
        cur.execute(
            "SELECT COUNT(*) AS jumlah FROM krs_detail kd JOIN krs k ON k.krs_id = kd.krs_id "
            "WHERE kd.kelas_id = %s AND k.status IN ('Diajukan','Disetujui')",
            (kelas_id,),
        )
        if cur.fetchone()["jumlah"] >= kelas["kuota"]:
            raise ValidationError("Kuota kelas sudah penuh.")
        cur.execute(
            "SELECT kd.krs_detail_id FROM krs_detail kd "
            "JOIN kelas existing ON existing.kelas_id = kd.kelas_id "
            "WHERE kd.krs_id = %s AND (kd.kelas_id = %s OR existing.mk_id = %s)",
            (krs["krs_id"], kelas_id, kelas["mk_id"]),
        )
        if cur.fetchone():
            raise ValidationError("Mata kuliah ini sudah ada pada KRS.")
        cur.execute(
            "INSERT INTO krs_detail (krs_id, kelas_id, status_ambil) VALUES (%s, %s, 'Baru')",
            (krs["krs_id"], kelas_id),
        )
        return cur.lastrowid


@require_role(MAHASISWA)
def hapus_kelas(krs_detail_id):
    mahasiswa_id = _mahasiswa_id()
    krs_detail_id = cek_id(krs_detail_id, "Detail KRS")
    semester = _semester_aktif()
    with db.db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT k.krs_id, k.status FROM krs_detail kd JOIN krs k ON k.krs_id = kd.krs_id "
            "WHERE kd.krs_detail_id = %s AND k.mahasiswa_id = %s AND k.semester_id = %s FOR UPDATE",
            (krs_detail_id, mahasiswa_id, semester["semester_id"]),
        )
        row = cur.fetchone()
        if row is None:
            raise ValidationError("Kelas tidak ditemukan pada KRS mahasiswa.")
        if row["status"] != "Draft":
            raise ValidationError("Kelas hanya dapat dihapus dari KRS berstatus Draft.")
        cur.execute("DELETE FROM krs_detail WHERE krs_detail_id = %s", (krs_detail_id,))


@require_role(MAHASISWA)
def ajukan():
    mahasiswa_id = _mahasiswa_id()
    semester = _semester_aktif()
    with db.db_cursor(commit=True) as cur:
        krs = _ambil_atau_buat_draft(cur, mahasiswa_id, semester["semester_id"])
        if krs["status"] != "Draft":
            raise ValidationError("KRS ini sudah diajukan atau disetujui.")
        cur.execute("SELECT COUNT(*) AS jumlah FROM krs_detail WHERE krs_id = %s", (krs["krs_id"],))
        if cur.fetchone()["jumlah"] == 0:
            raise ValidationError("Pilih minimal satu kelas sebelum mengajukan KRS.")
        cur.execute(
            "SELECT kl.kelas_id, kl.kuota FROM krs_detail kd "
            "JOIN kelas kl ON kl.kelas_id = kd.kelas_id "
            "WHERE kd.krs_id = %s ORDER BY kl.kelas_id FOR UPDATE",
            (krs["krs_id"],),
        )
        kelas_rows = cur.fetchall()
        for kelas in kelas_rows:
            cur.execute(
                "SELECT COUNT(*) AS jumlah FROM krs_detail kd JOIN krs k ON k.krs_id = kd.krs_id "
                "WHERE kd.kelas_id = %s AND k.krs_id <> %s AND k.status IN ('Diajukan','Disetujui')",
                (kelas["kelas_id"], krs["krs_id"]),
            )
            if cur.fetchone()["jumlah"] >= kelas["kuota"]:
                raise ValidationError(f"Kuota kelas {kelas['kelas_id']} sudah penuh; hapus dari KRS sebelum mengajukan.")
        cur.execute(
            "UPDATE krs SET status = 'Diajukan', tgl_pengajuan = NOW(), catatan_pa = NULL "
            "WHERE krs_id = %s",
            (krs["krs_id"],),
        )
    return krs["krs_id"]


@require_role(DOSEN)
def daftar_persetujuan():
    dosen_id = _dosen_id()
    return db.fetch_all(
        "SELECT k.krs_id, k.tgl_pengajuan, m.mahasiswa_id, m.nim, m.nama_lengkap, "
        "m.angkatan, p.nama_prodi, sa.kode_semester "
        "FROM krs k JOIN mahasiswa m ON m.mahasiswa_id = k.mahasiswa_id "
        "JOIN program_studi p ON p.prodi_id = m.prodi_id "
        "JOIN semester_akademik sa ON sa.semester_id = k.semester_id "
        "WHERE k.status = 'Diajukan' AND m.dosen_pa_id = %s "
        "ORDER BY k.tgl_pengajuan, m.nama_lengkap",
        (dosen_id,),
    )


@require_role(DOSEN)
def detail_persetujuan(krs_id):
    dosen_id = _dosen_id()
    krs_id = cek_id(krs_id, "KRS")
    krs = db.fetch_one(
        "SELECT k.krs_id, k.status, k.catatan_pa, m.mahasiswa_id, m.nim, "
        "m.nama_lengkap, m.angkatan, p.nama_prodi, sa.kode_semester "
        "FROM krs k JOIN mahasiswa m ON m.mahasiswa_id = k.mahasiswa_id "
        "JOIN program_studi p ON p.prodi_id = m.prodi_id "
        "JOIN semester_akademik sa ON sa.semester_id = k.semester_id "
        "WHERE k.krs_id = %s AND m.dosen_pa_id = %s",
        (krs_id, dosen_id),
    )
    if krs is None:
        raise ValidationError("KRS tidak ditemukan atau bukan tanggung jawab dosen ini.")
    items = db.fetch_all(
        "SELECT mk.kode_mk, mk.nama_mk, mk.sks, kl.nama_kelas "
        "FROM krs_detail kd JOIN kelas kl ON kl.kelas_id = kd.kelas_id "
        "JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id "
        "WHERE kd.krs_id = %s ORDER BY mk.kode_mk",
        (krs_id,),
    )
    return {"krs": krs, "detail": items}


@require_role(DOSEN)
def putuskan(krs_id, keputusan, catatan=None):
    dosen_id = _dosen_id()
    krs_id = cek_id(krs_id, "KRS")
    if keputusan not in ("Disetujui", "Ditolak"):
        raise ValidationError("Keputusan harus Disetujui atau Ditolak.")
    catatan = (catatan or "").strip() or None
    if catatan is not None and len(catatan) > 255:
        raise ValidationError("Catatan PA maksimal 255 karakter.")
    with db.db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT k.krs_id, k.status FROM krs k JOIN mahasiswa m ON m.mahasiswa_id = k.mahasiswa_id "
            "WHERE k.krs_id = %s AND m.dosen_pa_id = %s FOR UPDATE",
            (krs_id, dosen_id),
        )
        krs = cur.fetchone()
        if krs is None:
            raise ValidationError("KRS tidak ditemukan atau bukan tanggung jawab dosen ini.")
        if krs["status"] != "Diajukan":
            raise ValidationError("KRS ini sudah diproses atau belum diajukan.")
        cur.execute(
            "UPDATE krs SET status = %s, disetujui_oleh = %s, tgl_persetujuan = NOW(), "
            "catatan_pa = %s WHERE krs_id = %s",
            (keputusan, dosen_id, catatan, krs_id),
        )
    return krs_id
