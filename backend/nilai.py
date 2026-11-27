"""Input nilai langsung per mahasiswa, mata kuliah, dan semester."""

from database import connection as db
from utils import session
from utils.permissions import ADMIN, DOSEN, MAHASISWA, efektif_mahasiswa_id, require_role
from utils.validators import ValidationError, cek_id, cek_nilai


def _skala_untuk(nilai_angka):
    skala = db.fetch_one(
        "SELECT skala_id, huruf_mutu, bobot_mutu, is_lulus FROM skala_nilai "
        "WHERE %s BETWEEN nilai_min AND nilai_max",
        (nilai_angka,),
    )
    if skala is None:
        raise ValidationError("Nilai akhir tidak cocok dengan rentang skala nilai.")
    return skala


@require_role(ADMIN, DOSEN)
def daftar_skala():
    return db.fetch_all(
        "SELECT skala_id, huruf_mutu, bobot_mutu, nilai_min, nilai_max, is_lulus "
        "FROM skala_nilai ORDER BY nilai_min DESC"
    )


@require_role(ADMIN, DOSEN)
def pratinjau(nilai_angka):
    nilai_angka = cek_nilai(nilai_angka, "Nilai akhir")
    skala = _skala_untuk(nilai_angka)
    return {
        "nilai_akhir": nilai_angka,
        "huruf_mutu": skala["huruf_mutu"],
        "bobot_mutu": skala["bobot_mutu"],
        "is_lulus": bool(skala["is_lulus"]),
    }


def _prodi_dosen():
    dosen_id = session.get_user().get("dosen_id")
    if dosen_id is None:
        raise ValidationError("Akun dosen belum terhubung ke profil dosen.")
    dosen = db.fetch_one(
        "SELECT prodi_id FROM dosen WHERE dosen_id = %s AND status = 'Aktif'",
        (dosen_id,),
    )
    if dosen is None:
        raise ValidationError("Profil dosen tidak aktif atau tidak ditemukan.")
    if dosen["prodi_id"] is None:
        raise ValidationError("Profil dosen belum terhubung ke program studi.")
    return dosen_id, dosen["prodi_id"]


@require_role(DOSEN)
def mahasiswa_untuk_input():
    """Mahasiswa aktif pada program studi dosen yang sedang login."""
    _, prodi_id = _prodi_dosen()
    return db.fetch_all(
        "SELECT mahasiswa_id, nim, nama_lengkap, prodi_id "
        "FROM mahasiswa WHERE status_mahasiswa = 'Aktif' AND prodi_id = %s "
        "ORDER BY nama_lengkap, nim",
        (prodi_id,),
    )


@require_role(DOSEN)
def mata_kuliah_untuk_input(mahasiswa_id):
    """Mata kuliah dari kurikulum program studi mahasiswa yang dipilih."""
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    _, prodi_id_dosen = _prodi_dosen()
    mahasiswa = db.fetch_one(
        "SELECT prodi_id, status_mahasiswa FROM mahasiswa WHERE mahasiswa_id = %s",
        (mahasiswa_id,),
    )
    if mahasiswa is None or mahasiswa["status_mahasiswa"] != "Aktif":
        raise ValidationError("Mahasiswa aktif tidak ditemukan.")
    if int(mahasiswa["prodi_id"]) != int(prodi_id_dosen):
        raise ValidationError("Dosen hanya dapat menginput nilai untuk program studinya.")
    return db.fetch_all(
        "SELECT mk.mk_id, mk.kode_mk, mk.nama_mk, mk.sks, ku.nama_kurikulum "
        "FROM mata_kuliah mk JOIN kurikulum ku ON ku.kurikulum_id = mk.kurikulum_id "
        "WHERE ku.prodi_id = %s AND ku.is_aktif = TRUE "
        "ORDER BY mk.semester_paket, mk.kode_mk",
        (mahasiswa["prodi_id"],),
    )


@require_role(DOSEN)
def semester_untuk_input():
    return db.fetch_all(
        "SELECT semester_id, kode_semester, tahun_akademik "
        "FROM semester_akademik ORDER BY kode_semester DESC"
    )


@require_role(DOSEN)
def simpan(mahasiswa_id, mk_id, semester_id, nilai_angka):
    """Finalisasi nilai mahasiswa tanpa memerlukan pendaftaran KRS."""
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    mk_id = cek_id(mk_id, "Mata kuliah")
    semester_id = cek_id(semester_id, "Semester")
    nilai_angka = cek_nilai(nilai_angka, "Nilai akhir")
    dosen_id, prodi_id_dosen = _prodi_dosen()

    mahasiswa = db.fetch_one(
        "SELECT prodi_id, status_mahasiswa FROM mahasiswa WHERE mahasiswa_id = %s",
        (mahasiswa_id,),
    )
    if mahasiswa is None or mahasiswa["status_mahasiswa"] != "Aktif":
        raise ValidationError("Nilai hanya dapat dimasukkan untuk mahasiswa berstatus Aktif.")
    if int(mahasiswa["prodi_id"]) != int(prodi_id_dosen):
        raise ValidationError("Dosen hanya dapat menginput nilai untuk program studinya.")
    mata_kuliah = db.fetch_one(
        "SELECT mk.mk_id FROM mata_kuliah mk "
        "JOIN kurikulum ku ON ku.kurikulum_id = mk.kurikulum_id "
        "WHERE mk.mk_id = %s AND ku.prodi_id = %s",
        (mk_id, mahasiswa["prodi_id"]),
    )
    if mata_kuliah is None:
        raise ValidationError("Mata kuliah tidak terdaftar pada program studi mahasiswa.")
    if db.fetch_one(
        "SELECT semester_id FROM semester_akademik WHERE semester_id = %s",
        (semester_id,),
    ) is None:
        raise ValidationError("Semester tidak ditemukan.")

    nilai_lama = db.fetch_one(
        "SELECT is_final FROM nilai_mahasiswa "
        "WHERE mahasiswa_id = %s AND mk_id = %s AND semester_id = %s",
        (mahasiswa_id, mk_id, semester_id),
    )
    if nilai_lama and nilai_lama["is_final"]:
        raise ValidationError("Nilai sudah difinalisasi dan tidak dapat diubah.")
    skala = _skala_untuk(nilai_angka)
    db.execute(
        "INSERT INTO nilai_mahasiswa "
        "(mahasiswa_id, mk_id, semester_id, skala_id, nilai_angka, is_final, "
        "diinput_oleh, finalized_at) "
        "VALUES (%s, %s, %s, %s, %s, TRUE, %s, NOW()) "
        "ON DUPLICATE KEY UPDATE skala_id = VALUES(skala_id), "
        "nilai_angka = VALUES(nilai_angka), is_final = TRUE, "
        "diinput_oleh = VALUES(diinput_oleh), finalized_at = NOW()",
        (mahasiswa_id, mk_id, semester_id, skala["skala_id"], nilai_angka, dosen_id),
    )
    return {
        "mahasiswa_id": mahasiswa_id, "mk_id": mk_id,
        "semester_id": semester_id, "nilai_akhir": nilai_angka, **skala,
    }


@require_role(ADMIN, DOSEN, MAHASISWA)
def daftar(mahasiswa_id=None):
    """Daftar nilai final; mahasiswa otomatis hanya dapat membaca nilainya sendiri."""
    mahasiswa_id = efektif_mahasiswa_id(mahasiswa_id)
    if mahasiswa_id is None:
        raise ValidationError("Pilih mahasiswa terlebih dahulu.")
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    return db.fetch_all(
        "SELECT kode_semester, kode_mk, nama_mk, sks, nilai_akhir, huruf_mutu, "
        "bobot_mutu, status_kelulusan FROM v_transkrip "
        "WHERE mahasiswa_id = %s ORDER BY kode_semester, kode_mk",
        (mahasiswa_id,),
    )
