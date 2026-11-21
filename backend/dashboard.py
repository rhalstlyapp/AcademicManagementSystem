"""Ringkasan angka utama untuk dashboard sesuai tabel schema.sql."""
from database import connection as db
from utils.permissions import ADMIN, DOSEN, MAHASISWA, require_role


@require_role(ADMIN, DOSEN, MAHASISWA)
def ringkasan():
    """Ambil jumlah data pokok dan semester yang sedang aktif."""
    return db.fetch_one(
        "SELECT "
        "(SELECT COUNT(*) FROM mahasiswa) AS jumlah_mahasiswa, "
        "(SELECT COUNT(*) FROM dosen WHERE status = 'Aktif') AS jumlah_dosen_aktif, "
        "(SELECT COUNT(*) FROM program_studi) AS jumlah_prodi, "
        "(SELECT kode_semester FROM semester_akademik WHERE is_aktif = TRUE LIMIT 1) AS semester_aktif"
    )
