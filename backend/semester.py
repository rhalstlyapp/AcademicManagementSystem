"""CRUD semester akademik sesuai kolom wajib pada schema.sql."""
from datetime import date, datetime

from database import connection as db
from utils.permissions import ADMIN, require_role
from utils.validators import ValidationError, cek_id, cek_kode_semester

JENIS = {"1": "Ganjil", "2": "Genap", "3": "Pendek"}


def _tanggal(nilai, label):
    if isinstance(nilai, datetime):
        return nilai.date()
    if isinstance(nilai, date):
        return nilai
    try:
        return datetime.strptime(str(nilai).strip(), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValidationError(f"{label} harus berformat YYYY-MM-DD.") from None


def _turunkan(kode):
    tahun = int(kode[:4])
    return f"{tahun}/{tahun + 1}", JENIS[kode[4]]


@require_role(ADMIN)
def daftar():
    return db.fetch_all(
        "SELECT semester_id, kode_semester, tahun_akademik, jenis, tgl_mulai, "
        "tgl_selesai, tgl_mulai_krs, tgl_selesai_krs, is_aktif "
        "FROM semester_akademik ORDER BY kode_semester DESC"
    )


@require_role(ADMIN)
def tambah(kode_semester, tgl_mulai, tgl_selesai, tgl_mulai_krs, tgl_selesai_krs, is_aktif=False):
    kode = cek_kode_semester(kode_semester)
    if db.fetch_one("SELECT semester_id FROM semester_akademik WHERE kode_semester = %s", (kode,)):
        raise ValidationError("Kode semester sudah ada.")
    mulai = _tanggal(tgl_mulai, "Tanggal mulai")
    selesai = _tanggal(tgl_selesai, "Tanggal selesai")
    mulai_krs = _tanggal(tgl_mulai_krs, "Tanggal mulai KRS")
    selesai_krs = _tanggal(tgl_selesai_krs, "Tanggal selesai KRS")
    if selesai <= mulai:
        raise ValidationError("Tanggal selesai harus setelah tanggal mulai.")
    if selesai_krs < mulai_krs:
        raise ValidationError("Tanggal selesai KRS tidak boleh sebelum tanggal mulai KRS.")
    tahun_akademik, jenis = _turunkan(kode)
    with db.db_cursor(commit=True) as cur:
        if is_aktif:
            cur.execute("UPDATE semester_akademik SET is_aktif = FALSE WHERE is_aktif = TRUE")
        cur.execute(
            "INSERT INTO semester_akademik "
            "(kode_semester, tahun_akademik, jenis, tgl_mulai, tgl_selesai, "
            "tgl_mulai_krs, tgl_selesai_krs, is_aktif) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (kode, tahun_akademik, jenis, mulai, selesai, mulai_krs, selesai_krs, bool(is_aktif)),
        )
        return cur.lastrowid


@require_role(ADMIN)
def aktifkan(semester_id):
    semester_id = cek_id(semester_id, "Semester")
    with db.db_cursor(commit=True) as cur:
        cur.execute("SELECT semester_id FROM semester_akademik WHERE semester_id = %s", (semester_id,))
        if cur.fetchone() is None:
            raise ValidationError("Semester tidak ditemukan.")
        cur.execute("UPDATE semester_akademik SET is_aktif = FALSE WHERE is_aktif = TRUE")
        cur.execute("UPDATE semester_akademik SET is_aktif = TRUE WHERE semester_id = %s", (semester_id,))


@require_role(ADMIN)
def hapus(semester_id):
    semester_id = cek_id(semester_id, "Semester")
    row = db.fetch_one(
        "SELECT is_aktif FROM semester_akademik WHERE semester_id = %s", (semester_id,)
    )
    if row is None:
        raise ValidationError("Semester tidak ditemukan.")
    if row["is_aktif"]:
        raise ValidationError("Semester aktif tidak dapat dihapus.")
    references = db.fetch_one(
        "SELECT (SELECT COUNT(*) FROM krs WHERE semester_id = %s) + "
        "(SELECT COUNT(*) FROM kelas WHERE semester_id = %s) + "
        "(SELECT COUNT(*) FROM ip_semester WHERE semester_id = %s) AS jumlah",
        (semester_id, semester_id, semester_id),
    )
    if references["jumlah"]:
        raise ValidationError("Semester sudah dipakai KRS, kelas, atau perhitungan IP.")
    db.execute("DELETE FROM semester_akademik WHERE semester_id = %s", (semester_id,))
