"""Pengelolaan kelas kuliah dan penugasan dosen pengajar."""
from database import connection as db
from utils.permissions import ADMIN, require_role
from utils.validators import ValidationError, cek_id, cek_teks


def _bilangan_positif(nilai, label, maksimum):
    try:
        angka = int(str(nilai).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"{label} harus berupa angka bulat.") from None
    if not 1 <= angka <= maksimum:
        raise ValidationError(f"{label} harus antara 1 dan {maksimum}.")
    return angka


@require_role(ADMIN)
def daftar(semester_id=None, keyword=None):
    sql = (
        "SELECT kl.kelas_id, kl.nama_kelas, kl.kuota, mk.mk_id, mk.kode_mk, mk.nama_mk, "
        "mk.sks, sa.semester_id, sa.kode_semester, p.nama_prodi, "
        "(SELECT COUNT(*) FROM krs_detail kdd JOIN krs kr ON kr.krs_id = kdd.krs_id "
        "WHERE kdd.kelas_id = kl.kelas_id AND kr.status IN ('Diajukan','Disetujui')) AS jumlah_terdaftar, "
        "(SELECT GROUP_CONCAT(d.nama_lengkap ORDER BY d.nama_lengkap SEPARATOR ', ') "
        "FROM kelas_dosen kdx JOIN dosen d ON d.dosen_id = kdx.dosen_id "
        "WHERE kdx.kelas_id = kl.kelas_id) AS dosen_pengajar "
        "FROM kelas kl JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id "
        "JOIN kurikulum ku ON ku.kurikulum_id = mk.kurikulum_id "
        "JOIN program_studi p ON p.prodi_id = ku.prodi_id "
        "JOIN semester_akademik sa ON sa.semester_id = kl.semester_id WHERE 1 = 1"
    )
    params = []
    if semester_id is not None:
        sql += " AND kl.semester_id = %s"
        params.append(cek_id(semester_id, "Semester"))
    teks = (keyword or "").strip()
    if teks:
        pola = f"%{teks}%"
        sql += " AND (mk.kode_mk LIKE %s OR mk.nama_mk LIKE %s OR kl.nama_kelas LIKE %s)"
        params.extend((pola, pola, pola))
    return db.fetch_all(sql + " ORDER BY sa.kode_semester DESC, mk.kode_mk, kl.nama_kelas", tuple(params))


@require_role(ADMIN)
def tambah(mk_id, semester_id, nama_kelas, kuota, dosen_id):
    mk_id = cek_id(mk_id, "Mata kuliah")
    semester_id = cek_id(semester_id, "Semester")
    dosen_id = cek_id(dosen_id, "Dosen")
    nama_kelas = cek_teks(nama_kelas, "Nama kelas", 5).upper()
    kuota = _bilangan_positif(kuota, "Kuota", 65535)
    if db.fetch_one("SELECT mk_id FROM mata_kuliah WHERE mk_id = %s", (mk_id,)) is None:
        raise ValidationError("Mata kuliah tidak ditemukan.")
    if db.fetch_one("SELECT semester_id FROM semester_akademik WHERE semester_id = %s", (semester_id,)) is None:
        raise ValidationError("Semester tidak ditemukan.")
    if db.fetch_one(
        "SELECT dosen_id FROM dosen WHERE dosen_id = %s AND status = 'Aktif'", (dosen_id,)
    ) is None:
        raise ValidationError("Dosen pengajar harus berstatus Aktif.")
    if db.fetch_one(
        "SELECT kelas_id FROM kelas WHERE mk_id = %s AND semester_id = %s AND nama_kelas = %s",
        (mk_id, semester_id, nama_kelas),
    ):
        raise ValidationError("Nama kelas tersebut sudah ada untuk mata kuliah dan semester ini.")

    with db.db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO kelas (mk_id, semester_id, nama_kelas, kuota) VALUES (%s, %s, %s, %s)",
            (mk_id, semester_id, nama_kelas, kuota),
        )
        kelas_id = cur.lastrowid
        cur.execute(
            "INSERT INTO kelas_dosen (kelas_id, dosen_id, peran) VALUES (%s, %s, 'Koordinator')",
            (kelas_id, dosen_id),
        )
    return kelas_id


@require_role(ADMIN)
def hapus(kelas_id):
    kelas_id = cek_id(kelas_id, "Kelas")
    if db.fetch_one("SELECT kelas_id FROM kelas WHERE kelas_id = %s", (kelas_id,)) is None:
        raise ValidationError("Kelas tidak ditemukan.")
    dipakai = db.fetch_one(
        "SELECT COUNT(*) AS jumlah FROM krs_detail WHERE kelas_id = %s", (kelas_id,)
    )
    if dipakai["jumlah"]:
        raise ValidationError("Kelas sudah tercantum di KRS dan tidak dapat dihapus.")
    db.execute("DELETE FROM kelas WHERE kelas_id = %s", (kelas_id,))
