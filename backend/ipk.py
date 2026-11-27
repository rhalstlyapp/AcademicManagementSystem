"""IPS, IPK, dan transkrip. Perhitungan dilakukan oleh VIEW di database."""
from database import connection as db
from utils.permissions import ADMIN, efektif_nim, require_role
from utils.validators import ValidationError, cek_id, cek_nim, pola_cari


def _nim_diizinkan(nim):
    """Mahasiswa otomatis dibatasi ke data miliknya; admin wajib menyebut NIM."""
    efektif = efektif_nim(nim)
    if efektif is None:
        raise ValidationError("Pilih mahasiswa terlebih dahulu.")
    return cek_nim(efektif)


def ips_per_semester(nim=None):
    nim = _nim_diizinkan(nim)
    return db.fetch_all(
        "SELECT kode_semester, tahun_akademik, sks_diambil, sks_lulus, total_mutu, ips "
        "FROM v_ips WHERE nim = %s ORDER BY kode_semester",
        (nim,),
    )


def ipk(nim=None):
    """IPK mahasiswa, atau None bila belum punya nilai."""
    nim = _nim_diizinkan(nim)
    return db.fetch_one(
        "SELECT nim, nama_lengkap, total_sks, total_sks_lulus, total_mutu, ipk "
        "FROM v_ipk WHERE nim = %s",
        (nim,),
    )


def transkrip(nim=None):
    nim = _nim_diizinkan(nim)
    return db.fetch_all(
        "SELECT kode_mk, nama_mk, sks, kode_semester, nilai_akhir, huruf_mutu, "
        "bobot_mutu, mutu, status_kelulusan "
        "FROM v_transkrip WHERE nim = %s ORDER BY kode_semester, kode_mk",
        (nim,),
    )


def ringkasan(nim=None):
    """Semua data untuk halaman transkrip: profil, IPK, IPS per semester, dan daftar nilai."""
    nim = _nim_diizinkan(nim)
    profil = db.fetch_one(
        "SELECT m.nim, m.nama_lengkap, m.angkatan, p.nama_prodi, j.nama_jurusan "
        "FROM mahasiswa m "
        "JOIN program_studi p ON p.prodi_id = m.prodi_id "
        "JOIN jurusan j ON j.jurusan_id = p.jurusan_id "
        "WHERE m.nim = %s",
        (nim,),
    )
    if profil is None:
        raise ValidationError("Mahasiswa tidak ditemukan.")
    return {
        "profil": profil,
        "ipk": ipk(nim),
        "ips": ips_per_semester(nim),
        "transkrip": transkrip(nim),
    }


@require_role(ADMIN)
def daftar_ipk(keyword=None, prodi_id=None):
    """Seluruh mahasiswa beserta IPK-nya (None bila belum punya nilai)."""
    sql = (
        "SELECT m.nim, m.nama_lengkap, p.kode_prodi, "
        "v.total_sks, v.total_sks_lulus, v.ipk "
        "FROM mahasiswa m "
        "JOIN program_studi p ON p.prodi_id = m.prodi_id "
        "LEFT JOIN v_ipk v ON v.nim = m.nim WHERE 1 = 1"
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
