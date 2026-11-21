"""Akses master fakultas (tabel yang menjadi induk program_studi di schema.sql)."""
from database import connection as db
from utils.permissions import ADMIN, require_role
from utils.validators import ValidationError, cek_id


@require_role(ADMIN)
def daftar():
    return db.fetch_all(
        "SELECT fakultas_id, kode_fakultas, nama_fakultas "
        "FROM fakultas ORDER BY nama_fakultas"
    )


@require_role(ADMIN)
def detail(fakultas_id):
    fakultas_id = cek_id(fakultas_id, "Fakultas")
    row = db.fetch_one(
        "SELECT fakultas_id, kode_fakultas, nama_fakultas "
        "FROM fakultas WHERE fakultas_id = %s",
        (fakultas_id,),
    )
    if row is None:
        raise ValidationError("Fakultas tidak ditemukan.")
    return row
