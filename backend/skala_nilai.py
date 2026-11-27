"""Referensi rentang nilai dan bobot mutu."""
from database import connection as db
from utils.permissions import ADMIN, DOSEN, MAHASISWA, require_role


@require_role(ADMIN, DOSEN, MAHASISWA)
def daftar():
    return db.fetch_all(
        "SELECT skala_id, huruf_mutu, bobot_mutu, nilai_min, nilai_max, is_lulus "
        "FROM skala_nilai ORDER BY nilai_min DESC"
    )
