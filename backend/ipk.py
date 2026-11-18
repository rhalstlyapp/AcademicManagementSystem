"""IPS, IPK, dan transkrip. Perhitungan dilakukan oleh VIEW di database."""
from database import connection as db
from utils.permissions import ADMIN, efektif_mahasiswa_id, require_role
from utils.validators import ValidationError, cek_id, pola_cari


def _id_diizinkan(mahasiswa_id):
    """Mahasiswa otomatis dibatasi ke data miliknya; admin wajib menyebut mahasiswa."""
    efektif = efektif_mahasiswa_id(mahasiswa_id)
    if efektif is None:
        raise ValidationError("Pilih mahasiswa terlebih dahulu.")
    return cek_id(efektif, "Mahasiswa")


def ips_per_semester(mahasiswa_id=None):
    mahasiswa_id = _id_diizinkan(mahasiswa_id)
    return db.fetch_all(
        "SELECT kode_semester, tahun_akademik, sks_diambil, sks_lulus, total_mutu, ips "
        "FROM v_ips WHERE mahasiswa_id = %s ORDER BY kode_semester",
        (mahasiswa_id,),
    )


def ipk(mahasiswa_id=None):
    """IPK mahasiswa, atau None bila belum punya nilai."""
    mahasiswa_id = _id_diizinkan(mahasiswa_id)
    return db.fetch_one(
        "SELECT nim, nama_lengkap, total_sks, total_sks_lulus, total_mutu, ipk "
        "FROM v_ipk WHERE mahasiswa_id = %s",
        (mahasiswa_id,),
    )


def transkrip(mahasiswa_id=None):
    mahasiswa_id = _id_diizinkan(mahasiswa_id)
    return db.fetch_all(
        "SELECT kode_mk, nama_mk, sks, kode_semester, nilai_akhir, huruf_mutu, "
        "bobot_mutu, mutu, status_kelulusan "
        "FROM v_transkrip WHERE mahasiswa_id = %s ORDER BY kode_semester, kode_mk",
        (mahasiswa_id,),
    )


def ringkasan(mahasiswa_id=None):
    """Semua data untuk halaman transkrip: IPK, IPS per semester, dan daftar nilai."""
    mahasiswa_id = _id_diizinkan(mahasiswa_id)
    profil = db.fetch_one(
        "SELECT m.nim, m.nama_lengkap, m.angkatan, p.nama_prodi "
        "FROM mahasiswa m JOIN program_studi p ON p.prodi_id = m.prodi_id "
        "WHERE m.mahasiswa_id = %s",
        (mahasiswa_id,),
    )
    if profil is None:
        raise ValidationError("Mahasiswa tidak ditemukan.")
    return {
        "profil": profil,
        "ipk": ipk(mahasiswa_id),
        "ips": ips_per_semester(mahasiswa_id),
        "transkrip": transkrip(mahasiswa_id),
    }


@require_role(ADMIN)
def daftar_ipk(keyword=None, prodi_id=None):
    """Seluruh mahasiswa beserta IPK-nya (None bila belum punya nilai)."""
    sql = (
        "SELECT m.mahasiswa_id, m.nim, m.nama_lengkap, p.kode_prodi, "
        "v.total_sks, v.total_sks_lulus, v.ipk "
        "FROM mahasiswa m "
        "JOIN program_studi p ON p.prodi_id = m.prodi_id "
        "LEFT JOIN v_ipk v ON v.mahasiswa_id = m.mahasiswa_id WHERE 1 = 1"
    )
    params = []
    pola = pola_cari(keyword)
    if pola:
        sql += " AND (m.nim LIKE %s OR m.nama_lengkap LIKE %s)"
        params += [pola, pola]
    if prodi_id:
        sql += " AND m.prodi_id = %s"
        params.append(cek_id(prodi_id, "Program studi"))
    return db.fetch_all(sql + " ORDER BY m.nim", params)