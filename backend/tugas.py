"""Catatan tugas pribadi mahasiswa, dipisahkan berdasarkan akun."""
from datetime import date, datetime

from database import connection as db
from utils import session
from utils.permissions import MAHASISWA, require_role
from utils.validators import ValidationError, cek_wajib


def _mahasiswa_id():
    mahasiswa_id = session.get_user().get("mahasiswa_id")
    if mahasiswa_id is None:
        raise ValidationError("Akun belum terhubung ke profil mahasiswa.")
    return mahasiswa_id


def _tanggal(nilai):
    if isinstance(nilai, datetime):
        return nilai.date()
    if isinstance(nilai, date):
        return nilai
    try:
        return datetime.strptime(str(nilai).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Tanggal tugas harus berformat YYYY-MM-DD.") from None


@require_role(MAHASISWA)
def daftar_bulan(tahun, bulan):
    try:
        tahun, bulan = int(tahun), int(bulan)
        date(tahun, bulan, 1)
    except (TypeError, ValueError):
        raise ValidationError("Bulan kalender tidak valid.") from None
    return db.fetch_all(
        "SELECT tanggal, COUNT(*) AS jumlah, "
        "SUM(CASE WHEN selesai = TRUE THEN 1 ELSE 0 END) AS jumlah_selesai "
        "FROM tugas_mahasiswa WHERE mahasiswa_id = %s "
        "AND YEAR(tanggal) = %s AND MONTH(tanggal) = %s "
        "GROUP BY tanggal ORDER BY tanggal",
        (_mahasiswa_id(), tahun, bulan),
    )


@require_role(MAHASISWA)
def daftar_tanggal(tanggal):
    tanggal = _tanggal(tanggal)
    return db.fetch_all(
        "SELECT tugas_id, judul, catatan, tanggal, selesai "
        "FROM tugas_mahasiswa WHERE mahasiswa_id = %s AND tanggal = %s "
        "ORDER BY selesai, dibuat_pada, tugas_id",
        (_mahasiswa_id(), tanggal),
    )


@require_role(MAHASISWA)
def tambah(judul, tanggal, catatan=""):
    judul = cek_wajib(judul, "Judul tugas")
    if len(judul) > 180:
        raise ValidationError("Judul tugas maksimal 180 karakter.")
    catatan = (catatan or "").strip()
    if len(catatan) > 1000:
        raise ValidationError("Catatan tugas maksimal 1000 karakter.")
    tanggal = _tanggal(tanggal)
    with db.db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO tugas_mahasiswa (mahasiswa_id, judul, catatan, tanggal) "
            "VALUES (%s, %s, %s, %s)",
            (_mahasiswa_id(), judul, catatan or None, tanggal),
        )
        return cur.lastrowid


@require_role(MAHASISWA)
def ubah_selesai(tugas_id, selesai):
    try:
        tugas_id = int(tugas_id)
    except (TypeError, ValueError):
        raise ValidationError("Tugas tidak valid.") from None
    if tugas_id <= 0:
        raise ValidationError("Tugas tidak valid.")
    with db.db_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE tugas_mahasiswa SET selesai = %s "
            "WHERE tugas_id = %s AND mahasiswa_id = %s",
            (bool(selesai), tugas_id, _mahasiswa_id()),
        )
        if cur.rowcount == 0:
            cur.execute(
                "SELECT tugas_id FROM tugas_mahasiswa "
                "WHERE tugas_id = %s AND mahasiswa_id = %s",
                (tugas_id, _mahasiswa_id()),
            )
            if cur.fetchone() is None:
                raise ValidationError("Tugas tidak ditemukan.")


@require_role(MAHASISWA)
def hapus(tugas_id):
    try:
        tugas_id = int(tugas_id)
    except (TypeError, ValueError):
        raise ValidationError("Tugas tidak valid.") from None
    if tugas_id <= 0:
        raise ValidationError("Tugas tidak valid.")
    with db.db_cursor(commit=True) as cur:
        cur.execute(
            "DELETE FROM tugas_mahasiswa WHERE tugas_id = %s AND mahasiswa_id = %s",
            (tugas_id, _mahasiswa_id()),
        )
        if cur.rowcount == 0:
            raise ValidationError("Tugas tidak ditemukan.")
