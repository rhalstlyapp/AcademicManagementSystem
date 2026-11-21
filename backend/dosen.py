"""Pembuatan akun dan pengelolaan profil dosen."""
from database import connection as db
from utils.permissions import ADMIN, require_role
from utils.security import hash_password
from utils.validators import (
    ValidationError,
    cek_id,
    cek_nama_orang,
    cek_password,
    cek_pilihan,
    cek_username,
    cek_wajib,
    pola_cari,
)

STATUS_DOSEN = ("Aktif", "Cuti", "Pensiun", "Keluar")


@require_role(ADMIN)
def daftar(keyword=None, status=None):
    sql = (
        "SELECT d.dosen_id, d.user_id, u.username, u.email, d.nidn, d.nip, "
        "d.nama_lengkap, d.jenis_kelamin, d.status, p.prodi_id, p.kode_prodi, "
        "p.nama_prodi, j.jurusan_id, j.nama_jurusan "
        "FROM dosen d JOIN users u ON u.user_id = d.user_id "
        "JOIN program_studi p ON p.prodi_id = d.prodi_id "
        "JOIN jurusan j ON j.jurusan_id = p.jurusan_id WHERE 1 = 1"
    )
    params = []
    pola = pola_cari(keyword)
    if pola:
        sql += " AND (d.nama_lengkap LIKE %s OR d.nidn LIKE %s OR d.nip LIKE %s OR u.username LIKE %s)"
        params.extend((pola, pola, pola, pola))
    if status:
        status = cek_pilihan(status, STATUS_DOSEN, "Status dosen")
        sql += " AND d.status = %s"
        params.append(status)
    return db.fetch_all(sql + " ORDER BY d.nama_lengkap", tuple(params))


@require_role(ADMIN)
def tambah(username, email, password, nama, prodi_id, jenis_kelamin, nidn=None, nip=None):
    username = cek_username(username)
    email = cek_wajib(email, "Email").strip()
    if "@" not in email or len(email) > 100:
        raise ValidationError("Email tidak valid.")
    password = cek_password(password)
    nama = cek_nama_orang(nama, "Nama dosen")
    prodi_id = cek_id(prodi_id, "Program studi")
    jenis_kelamin = cek_pilihan((jenis_kelamin or "").strip().upper(), ("L", "P"), "Jenis kelamin")

    nidn = str(nidn or "").strip() or None
    nip = str(nip or "").strip() or None
    if nidn is None and nip is None:
        raise ValidationError("Isi NIDN atau NIP dosen.")
    if nidn is not None and (not nidn.isdigit() or len(nidn) > 10):
        raise ValidationError("NIDN harus berisi maksimal 10 angka.")
    if nip is not None and (not nip.isdigit() or len(nip) > 18):
        raise ValidationError("NIP harus berisi maksimal 18 angka.")
    if db.fetch_one("SELECT prodi_id FROM program_studi WHERE prodi_id = %s", (prodi_id,)) is None:
        raise ValidationError("Program studi tidak ditemukan.")

    with db.db_cursor(commit=True) as cur:
        cur.execute("SELECT role_id FROM roles WHERE nama_role = %s", ("dosen",))
        role = cur.fetchone()
        if role is None:
            raise ValidationError("Role dosen belum tersedia. Jalankan database/seed.sql.")
        cur.execute(
            "INSERT INTO users (role_id, username, email, password_hash, is_active) "
            "VALUES (%s, %s, %s, %s, TRUE)",
            (role["role_id"], username, email, hash_password(password)),
        )
        user_id = cur.lastrowid
        cur.execute(
            "INSERT INTO dosen (user_id, prodi_id, nidn, nip, nama_lengkap, jenis_kelamin, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, 'Aktif')",
            (user_id, prodi_id, nidn, nip, nama, jenis_kelamin),
        )
        return cur.lastrowid


@require_role(ADMIN)
def ubah_status(dosen_id, status):
    dosen_id = cek_id(dosen_id, "Dosen")
    status = cek_pilihan(status, STATUS_DOSEN, "Status dosen")
    with db.db_cursor(commit=True) as cur:
        cur.execute("SELECT user_id FROM dosen WHERE dosen_id = %s", (dosen_id,))
        dosen = cur.fetchone()
        if dosen is None:
            raise ValidationError("Dosen tidak ditemukan.")
        cur.execute("UPDATE dosen SET status = %s WHERE dosen_id = %s", (status, dosen_id))
        cur.execute(
            "UPDATE users SET is_active = %s WHERE user_id = %s",
            (status not in ("Pensiun", "Keluar"), dosen["user_id"]),
        )
    return dosen_id
