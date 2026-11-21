"""
backend/jurusan.py

Menangani data jurusan:
- Menampilkan semua jurusan
- Mengambil satu jurusan
- Menambahkan jurusan
- Mengubah jurusan
- Menghapus jurusan
"""

from database import connection as db
from utils.permissions import ADMIN, require_role

from utils.validators import (
    ValidationError,
    cek_kode_semester,
    cek_teks,
    cek_wajib,
    pola_cari,
)


# ============================================================
# DAFTAR JURUSAN
# ============================================================

@require_role(ADMIN)
def daftar_jurusan():
    """
    Mengambil semua data jurusan.
    """

    return db.fetch_all(
        """
        SELECT
            jurusan_id,
            kode_jurusan,
            nama_jurusan
        FROM jurusan
        ORDER BY nama_jurusan
        """
    )


# ============================================================
# CARI JURUSAN
# ============================================================

@require_role(ADMIN)
def cari_jurusan(keyword):
    """
    Mencari jurusan berdasarkan kode atau nama.
    """

    keyword = pola_cari(keyword)

    return db.fetch_all(
        """
        SELECT
            jurusan_id,
            kode_jurusan,
            nama_jurusan
        FROM jurusan
        WHERE kode_jurusan LIKE %s
           OR nama_jurusan LIKE %s
        ORDER BY nama_jurusan
        """,
        (keyword, keyword)
    )


# ============================================================
# AMBIL SATU JURUSAN
# ============================================================

@require_role(ADMIN)
def ambil_jurusan(jurusan_id):
    """
    Mengambil satu jurusan berdasarkan ID.
    """

    return db.fetch_one(
        """
        SELECT
            jurusan_id,
            kode_jurusan,
            nama_jurusan
        FROM jurusan
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )


# ============================================================
# TAMBAH JURUSAN
# ============================================================

@require_role(ADMIN)
def tambah_jurusan(kode_jurusan, nama_jurusan):
    """
    Menambahkan jurusan baru.
    """

    cek_wajib(kode_jurusan, "Kode jurusan")
    cek_wajib(nama_jurusan, "Nama jurusan")

    kode_jurusan = kode_jurusan.strip().upper()
    nama_jurusan = cek_teks(nama_jurusan, "Nama jurusan", 100)

    # Cek apakah kode sudah digunakan
    existing = db.fetch_one(
        """
        SELECT jurusan_id
        FROM jurusan
        WHERE kode_jurusan = %s
        """,
        (kode_jurusan,)
    )

    if existing is not None:
        raise ValidationError(
            "Kode jurusan sudah digunakan."
        )

    return db.execute(
        """
        INSERT INTO jurusan
            (kode_jurusan, nama_jurusan)
        VALUES
            (%s, %s)
        """,
        (kode_jurusan, nama_jurusan)
    )


# ============================================================
# UBAH JURUSAN
# ============================================================

@require_role(ADMIN)
def ubah_jurusan(jurusan_id, kode_jurusan, nama_jurusan):
    """
    Mengubah data jurusan.
    """

    cek_wajib(kode_jurusan, "Kode jurusan")
    cek_wajib(nama_jurusan, "Nama jurusan")

    kode_jurusan = kode_jurusan.strip().upper()
    nama_jurusan = cek_teks(nama_jurusan, "Nama jurusan", 100)

    # Pastikan jurusan ada
    existing = db.fetch_one(
        """
        SELECT jurusan_id
        FROM jurusan
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )

    if existing is None:
        raise ValidationError(
            "Jurusan tidak ditemukan."
        )

    # Cek kode dipakai jurusan lain
    kode_dipakai = db.fetch_one(
        """
        SELECT jurusan_id
        FROM jurusan
        WHERE kode_jurusan = %s
          AND jurusan_id <> %s
        """,
        (kode_jurusan, jurusan_id)
    )

    if kode_dipakai is not None:
        raise ValidationError(
            "Kode jurusan sudah digunakan."
        )

    db.execute(
        """
        UPDATE jurusan
        SET
            kode_jurusan = %s,
            nama_jurusan = %s
        WHERE jurusan_id = %s
        """,
        (kode_jurusan, nama_jurusan, jurusan_id)
    )

    return True


# ============================================================
# HAPUS JURUSAN
# ============================================================

@require_role(ADMIN)
def hapus_jurusan(jurusan_id):
    """
    Menghapus jurusan.

    Jurusan yang masih mempunyai program studi
    tidak dapat dihapus karena terhubung dengan FK.
    """

    existing = db.fetch_one(
        """
        SELECT jurusan_id
        FROM jurusan
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )

    if existing is None:
        raise ValidationError(
            "Jurusan tidak ditemukan."
        )

    # Cek apakah masih mempunyai prodi
    jumlah_prodi = db.fetch_one(
        """
        SELECT COUNT(*) AS jumlah
        FROM program_studi
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )

    if jumlah_prodi["jumlah"] > 0:
        raise ValidationError(
            "Jurusan tidak dapat dihapus karena masih memiliki "
            "program studi."
        )

    db.execute(
        """
        DELETE FROM jurusan
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )

    return True
