"""
backend/prodi.py

Menangani data program studi:
- Menampilkan semua prodi
- Mengambil satu prodi
- Mencari prodi
- Menambahkan prodi
- Mengubah prodi
- Menghapus prodi
"""

from database import connection as db
from utils.permissions import ADMIN, require_role

from utils.validators import (
    ValidationError,
    cek_id,
    cek_teks,
    cek_wajib,
    pola_cari,
)


# ============================================================
# DAFTAR PRODI
# ============================================================

@require_role(ADMIN)
def daftar_prodi():
    """
    Mengambil semua program studi
    beserta informasi jurusannya.
    """

    return db.fetch_all(
        """
        SELECT
            ps.prodi_id,
            ps.jurusan_id,
            j.kode_jurusan,
            j.nama_jurusan,
            ps.kode_prodi,
            ps.nama_prodi,
            ps.jenjang
        FROM program_studi ps
        JOIN jurusan j
            ON j.jurusan_id = ps.jurusan_id
        WHERE ps.jenjang IN ('D3', 'D4')
        ORDER BY j.nama_jurusan, ps.jenjang, ps.nama_prodi
        """
    )


# ============================================================
# CARI PRODI
# ============================================================

@require_role(ADMIN)
def cari_prodi(keyword):
    """
    Mencari prodi berdasarkan:
    - kode prodi
    - nama prodi
    - nama jurusan
    """

    keyword = pola_cari(keyword)

    return db.fetch_all(
        """
        SELECT
            ps.prodi_id,
            ps.jurusan_id,
            j.kode_jurusan,
            j.nama_jurusan,
            ps.kode_prodi,
            ps.nama_prodi,
            ps.jenjang
        FROM program_studi ps
        JOIN jurusan j
            ON j.jurusan_id = ps.jurusan_id
        WHERE (ps.kode_prodi LIKE %s
           OR ps.nama_prodi LIKE %s
           OR j.nama_jurusan LIKE %s)
          AND ps.jenjang IN ('D3', 'D4')
        ORDER BY j.nama_jurusan, ps.jenjang, ps.nama_prodi
        """,
        (keyword, keyword, keyword)
    )


# ============================================================
# AMBIL SATU PRODI
# ============================================================

@require_role(ADMIN)
def ambil_prodi(prodi_id):
    """
    Mengambil satu program studi berdasarkan ID.
    """

    prodi_id = cek_id(prodi_id, "ID Program Studi")

    return db.fetch_one(
        """
        SELECT
            ps.prodi_id,
            ps.jurusan_id,
            j.kode_jurusan,
            j.nama_jurusan,
            ps.kode_prodi,
            ps.nama_prodi,
            ps.jenjang
        FROM program_studi ps
        JOIN jurusan j
            ON j.jurusan_id = ps.jurusan_id
        WHERE ps.prodi_id = %s AND ps.jenjang IN ('D3', 'D4')
        """,
        (prodi_id,)
    )


# ============================================================
# TAMBAH PRODI
# ============================================================

@require_role(ADMIN)
def tambah_prodi(
    jurusan_id,
    kode_prodi,
    nama_prodi,
    jenjang="D3"
):
    """
    Menambahkan program studi baru.
    """

    cek_wajib(jurusan_id, "Jurusan")
    cek_wajib(kode_prodi, "Kode prodi")
    cek_wajib(nama_prodi, "Nama prodi")
    cek_wajib(jenjang, "Jenjang")

    jurusan_id = cek_id(jurusan_id, "ID Jurusan")

    kode_prodi = kode_prodi.strip().upper()
    nama_prodi = cek_teks(
        nama_prodi,
        "Nama prodi",
        100
    )

    jenjang = jenjang.strip().upper()

    jenjang_valid = ("D3", "D4")

    if jenjang not in jenjang_valid:
        raise ValidationError("Jenjang program studi hanya D3 atau D4.")

    # Pastikan jurusan tersedia
    jurusan = db.fetch_one(
        """
        SELECT jurusan_id
        FROM jurusan
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )

    if jurusan is None:
        raise ValidationError(
            "Jurusan tidak ditemukan."
        )

    # Cek kode prodi
    existing = db.fetch_one(
        """
        SELECT prodi_id
        FROM program_studi
        WHERE kode_prodi = %s
        """,
        (kode_prodi,)
    )

    if existing is not None:
        raise ValidationError(
            "Kode program studi sudah digunakan."
        )

    return db.execute(
        """
        INSERT INTO program_studi
            (
                jurusan_id,
                kode_prodi,
                nama_prodi,
                jenjang
            )
        VALUES
            (%s, %s, %s, %s)
        """,
        (
            jurusan_id,
            kode_prodi,
            nama_prodi,
            jenjang,
        )
    )


# ============================================================
# UBAH PRODI
# ============================================================

@require_role(ADMIN)
def ubah_prodi(
    prodi_id,
    jurusan_id,
    kode_prodi,
    nama_prodi,
    jenjang
):
    """
    Mengubah data program studi.
    """

    cek_wajib(prodi_id, "ID Program Studi")
    cek_wajib(jurusan_id, "Jurusan")
    cek_wajib(kode_prodi, "Kode prodi")
    cek_wajib(nama_prodi, "Nama prodi")
    cek_wajib(jenjang, "Jenjang")

    prodi_id = cek_id(
        prodi_id,
        "ID Program Studi"
    )

    jurusan_id = cek_id(
        jurusan_id,
        "ID Jurusan"
    )

    kode_prodi = kode_prodi.strip().upper()

    nama_prodi = cek_teks(
        nama_prodi,
        "Nama prodi",
        100
    )

    jenjang = jenjang.strip().upper()

    if jenjang not in ("D3", "D4"):
        raise ValidationError("Jenjang program studi hanya D3 atau D4.")

    # Pastikan prodi ada
    existing = db.fetch_one(
        """
        SELECT prodi_id
        FROM program_studi
        WHERE prodi_id = %s
        """,
        (prodi_id,)
    )

    if existing is None:
        raise ValidationError(
            "Program studi tidak ditemukan."
        )

    # Pastikan jurusan ada
    jurusan = db.fetch_one(
        """
        SELECT jurusan_id
        FROM jurusan
        WHERE jurusan_id = %s
        """,
        (jurusan_id,)
    )

    if jurusan is None:
        raise ValidationError(
            "Jurusan tidak ditemukan."
        )

    # Cek apakah kode prodi dipakai prodi lain
    kode_dipakai = db.fetch_one(
        """
        SELECT prodi_id
        FROM program_studi
        WHERE kode_prodi = %s
          AND prodi_id <> %s
        """,
        (
            kode_prodi,
            prodi_id,
        )
    )

    if kode_dipakai is not None:
        raise ValidationError(
            "Kode program studi sudah digunakan."
        )

    db.execute(
        """
        UPDATE program_studi
        SET
            jurusan_id = %s,
            kode_prodi = %s,
            nama_prodi = %s,
            jenjang = %s
        WHERE prodi_id = %s
        """,
        (
            jurusan_id,
            kode_prodi,
            nama_prodi,
            jenjang,
            prodi_id,
        )
    )

    return True


# ============================================================
# HAPUS PRODI
# ============================================================

@require_role(ADMIN)
def hapus_prodi(prodi_id):
    """
    Menghapus program studi.

    Prodi yang masih digunakan oleh mahasiswa
    tidak dapat dihapus.
    """

    prodi_id = cek_id(
        prodi_id,
        "ID Program Studi"
    )

    # Pastikan prodi ada
    existing = db.fetch_one(
        """
        SELECT prodi_id
        FROM program_studi
        WHERE prodi_id = %s
        """,
        (prodi_id,)
    )

    if existing is None:
        raise ValidationError(
            "Program studi tidak ditemukan."
        )

    # Cek mahasiswa yang menggunakan prodi
    jumlah_mahasiswa = db.fetch_one(
        """
        SELECT COUNT(*) AS jumlah
        FROM mahasiswa
        WHERE prodi_id = %s
        """,
        (prodi_id,)
    )

    if jumlah_mahasiswa["jumlah"] > 0:
        raise ValidationError(
            "Program studi tidak dapat dihapus karena "
            "masih memiliki mahasiswa."
        )

    db.execute(
        """
        DELETE FROM program_studi
        WHERE prodi_id = %s
        """,
        (prodi_id,)
    )

    return True
