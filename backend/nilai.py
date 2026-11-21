"""Input nilai akhir melalui krs_detail/nilai_akhir dan baca transkrip."""

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


@require_role(DOSEN)
def daftar_krs_untuk_input():
    """KRS disetujui yang dapat diberi nilai oleh dosen yang sedang login."""
    dosen_id = session.get_user().get("dosen_id")
    if dosen_id is None:
        raise ValidationError("Akun dosen belum terhubung ke profil dosen.")
    return db.fetch_all(
        "SELECT kd.krs_detail_id, m.mahasiswa_id, m.nim, m.nama_lengkap, "
        "mk.kode_mk, mk.nama_mk, sa.kode_semester "
        "FROM kelas_dosen kdosen "
        "JOIN kelas kl ON kl.kelas_id = kdosen.kelas_id "
        "JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id "
        "JOIN semester_akademik sa ON sa.semester_id = kl.semester_id "
        "JOIN krs k ON k.semester_id = kl.semester_id AND k.status = 'Disetujui' "
        "JOIN mahasiswa m ON m.mahasiswa_id = k.mahasiswa_id AND m.status_mahasiswa = 'Aktif' "
        "JOIN krs_detail kd ON kd.krs_id = k.krs_id AND kd.kelas_id = kl.kelas_id "
        "LEFT JOIN nilai_akhir na ON na.krs_detail_id = kd.krs_detail_id "
        "WHERE kdosen.dosen_id = %s AND (na.krs_detail_id IS NULL OR na.is_final = FALSE) "
        "ORDER BY sa.kode_semester, mk.kode_mk, m.nim",
        (dosen_id,),
    )


@require_role(DOSEN)
def simpan(krs_detail_id, nilai_angka):
    """Finalisasi nilai untuk mata kuliah yang tercantum pada KRS disetujui."""
    krs_detail_id = cek_id(krs_detail_id, "Detail KRS")
    nilai_angka = cek_nilai(nilai_angka, "Nilai akhir")
    dosen_id = session.get_user().get("dosen_id")
    if dosen_id is None:
        raise ValidationError("Akun dosen belum terhubung ke profil dosen.")

    kelas = db.fetch_one(
        "SELECT kd.krs_detail_id, k.status AS status_krs, m.status_mahasiswa "
        "FROM krs_detail kd JOIN krs k ON k.krs_id = kd.krs_id "
        "JOIN mahasiswa m ON m.mahasiswa_id = k.mahasiswa_id "
        "JOIN kelas_dosen kdosen ON kdosen.kelas_id = kd.kelas_id "
        "WHERE kd.krs_detail_id = %s AND kdosen.dosen_id = %s",
        (krs_detail_id, dosen_id),
    )
    if kelas is None:
        raise ValidationError("Mata kuliah tidak ditemukan pada KRS mahasiswa.")
    if kelas["status_krs"] != "Disetujui":
        raise ValidationError("Nilai hanya dapat dimasukkan untuk KRS yang disetujui.")
    if kelas["status_mahasiswa"] != "Aktif":
        raise ValidationError("Nilai hanya dapat dimasukkan untuk mahasiswa berstatus Aktif.")

    nilai_lama = db.fetch_one(
        "SELECT is_final FROM nilai_akhir WHERE krs_detail_id = %s",
        (krs_detail_id,),
    )
    if nilai_lama and nilai_lama["is_final"]:
        raise ValidationError("Nilai sudah difinalisasi dan tidak dapat diubah.")
    skala = _skala_untuk(nilai_angka)
    db.execute(
        "INSERT INTO nilai_akhir "
        "(krs_detail_id, skala_id, nilai_angka, is_final, diinput_oleh, finalized_at) "
        "VALUES (%s, %s, %s, TRUE, %s, NOW()) "
        "ON DUPLICATE KEY UPDATE skala_id = VALUES(skala_id), "
        "nilai_angka = VALUES(nilai_angka), is_final = TRUE, "
        "diinput_oleh = VALUES(diinput_oleh), finalized_at = NOW()",
        (krs_detail_id, skala["skala_id"], nilai_angka, dosen_id),
    )
    return {"krs_detail_id": krs_detail_id, "nilai_akhir": nilai_angka, **skala}


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
