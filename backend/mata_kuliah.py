"""CRUD mata kuliah yang terhubung ke kurikulum dan program studi."""
from database import connection as db
from utils.permissions import ADMIN, require_role
from utils.validators import ValidationError, cek_id, cek_sks, cek_teks, pola_cari

JENIS_MK = ("Wajib", "Pilihan")

_SELECT = (
    "SELECT mk.mk_id, mk.kurikulum_id, mk.kode_mk, mk.nama_mk, mk.sks, "
    "mk.semester_paket, mk.jenis_mk, k.nama_kurikulum, p.prodi_id, "
    "p.kode_prodi, p.nama_prodi "
    "FROM mata_kuliah mk JOIN kurikulum k ON k.kurikulum_id = mk.kurikulum_id "
    "JOIN program_studi p ON p.prodi_id = k.prodi_id"
)


@require_role(ADMIN)
def daftar_kurikulum(prodi_id=None):
    sql = (
        "SELECT k.kurikulum_id, k.nama_kurikulum, k.tahun_berlaku, k.is_aktif, "
        "p.prodi_id, p.kode_prodi, p.nama_prodi "
        "FROM kurikulum k JOIN program_studi p ON p.prodi_id = k.prodi_id"
    )
    params = ()
    if prodi_id is not None:
        sql += " WHERE p.prodi_id = %s"
        params = (cek_id(prodi_id, "Program studi"),)
    return db.fetch_all(sql + " ORDER BY p.nama_prodi, k.tahun_berlaku DESC", params)


@require_role(ADMIN)
def daftar(keyword=None, prodi_id=None):
    sql = _SELECT + " WHERE 1 = 1"
    params = []
    pola = pola_cari(keyword)
    if pola:
        sql += " AND (mk.kode_mk LIKE %s OR mk.nama_mk LIKE %s)"
        params.extend((pola, pola))
    if prodi_id is not None:
        sql += " AND p.prodi_id = %s"
        params.append(cek_id(prodi_id, "Program studi"))
    return db.fetch_all(sql + " ORDER BY p.nama_prodi, mk.semester_paket, mk.kode_mk", tuple(params))


def _validasi(kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk):
    kurikulum_id = cek_id(kurikulum_id, "Kurikulum")
    if db.fetch_one("SELECT kurikulum_id FROM kurikulum WHERE kurikulum_id = %s", (kurikulum_id,)) is None:
        raise ValidationError("Kurikulum tidak ditemukan.")
    kode = cek_teks(kode_mk, "Kode mata kuliah", 15).upper()
    nama = cek_teks(nama_mk, "Nama mata kuliah", 150)
    sks = cek_sks(sks)
    try:
        paket = int(semester_paket)
    except (TypeError, ValueError):
        raise ValidationError("Semester paket harus berupa angka 1-8.") from None
    if not 1 <= paket <= 8:
        raise ValidationError("Semester paket harus antara 1 dan 8.")
    if jenis_mk not in JENIS_MK:
        raise ValidationError("Jenis mata kuliah harus Wajib atau Pilihan.")
    return kurikulum_id, kode, nama, sks, paket, jenis_mk


def _kode_dipakai(kode, kecuali_id=None):
    sql = "SELECT mk_id FROM mata_kuliah WHERE kode_mk = %s"
    params = [kode]
    if kecuali_id is not None:
        sql += " AND mk_id <> %s"
        params.append(kecuali_id)
    return db.fetch_one(sql, tuple(params)) is not None


@require_role(ADMIN)
def tambah(kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk="Wajib"):
    values = _validasi(kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk)
    if _kode_dipakai(values[1]):
        raise ValidationError("Kode mata kuliah sudah dipakai.")
    return db.execute(
        "INSERT INTO mata_kuliah "
        "(kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        values,
    )


@require_role(ADMIN)
def ubah(mk_id, kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk):
    mk_id = cek_id(mk_id, "Mata kuliah")
    if db.fetch_one("SELECT mk_id FROM mata_kuliah WHERE mk_id = %s", (mk_id,)) is None:
        raise ValidationError("Mata kuliah tidak ditemukan.")
    values = _validasi(kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk)
    if _kode_dipakai(values[1], mk_id):
        raise ValidationError("Kode mata kuliah sudah dipakai.")
    db.execute(
        "UPDATE mata_kuliah SET kurikulum_id = %s, kode_mk = %s, nama_mk = %s, "
        "sks = %s, semester_paket = %s, jenis_mk = %s WHERE mk_id = %s",
        (*values, mk_id),
    )


@require_role(ADMIN)
def hapus(mk_id):
    mk_id = cek_id(mk_id, "Mata kuliah")
    if db.fetch_one("SELECT mk_id FROM mata_kuliah WHERE mk_id = %s", (mk_id,)) is None:
        raise ValidationError("Mata kuliah tidak ditemukan.")
    references = db.fetch_one(
        "SELECT (SELECT COUNT(*) FROM kelas WHERE mk_id = %s) + "
        "(SELECT COUNT(*) FROM prasyarat_mk WHERE mk_id = %s OR mk_prasyarat_id = %s) AS jumlah",
        (mk_id, mk_id, mk_id),
    )
    if references["jumlah"]:
        raise ValidationError("Mata kuliah sudah dipakai kelas atau prasyarat dan tidak dapat dihapus.")
    db.execute("DELETE FROM mata_kuliah WHERE mk_id = %s", (mk_id,))
