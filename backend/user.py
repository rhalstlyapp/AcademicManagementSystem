"""Manajemen akun login."""
from database import connection as db
from utils import session
from utils.permissions import ADMIN, require_role
from utils.security import hash_password, verify_password
from utils.validators import (
    AuthError, ValidationError, cek_id, cek_password, cek_username, pola_cari,
)


@require_role(ADMIN)
def daftar(keyword=None):
    sql = """
        SELECT u.user_id, u.username, u.role, u.is_active, u.last_login_at, u.created_at,
               m.nim, m.nama_lengkap
        FROM users u
        LEFT JOIN mahasiswa m ON m.mahasiswa_id = u.mahasiswa_id
        WHERE 1 = 1
    """
    params = []
    pola = pola_cari(keyword)
    if pola:
        sql += " AND (u.username LIKE %s OR m.nama_lengkap LIKE %s OR m.nim LIKE %s)"
        params += [pola, pola, pola]
    sql += " ORDER BY u.role, u.username"
    return db.fetch_all(sql, params)


@require_role(ADMIN)
def buat_akun_mahasiswa(mahasiswa_id, password, username=None):
    """Membuat akun login untuk mahasiswa. Username bawaan: NIM."""
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    mhs = db.fetch_one("SELECT nim FROM mahasiswa WHERE mahasiswa_id = %s", (mahasiswa_id,))
    if mhs is None:
        raise ValidationError("Mahasiswa tidak ditemukan.")
    if db.fetch_one("SELECT user_id FROM users WHERE mahasiswa_id = %s", (mahasiswa_id,)):
        raise ValidationError("Mahasiswa ini sudah memiliki akun.")

    username = cek_username(username or mhs["nim"])
    if db.fetch_one("SELECT user_id FROM users WHERE username = %s", (username,)):
        raise ValidationError("Username sudah dipakai.")

    password_hash = hash_password(cek_password(password))
    return db.execute(
        "INSERT INTO users (mahasiswa_id, username, password_hash, role, is_active) "
        "VALUES (%s, %s, %s, 'mahasiswa', 1)",
        (mahasiswa_id, username, password_hash),
    )


@require_role(ADMIN)
def reset_password(user_id, password_baru):
    user_id = cek_id(user_id, "Akun")
    if db.fetch_one("SELECT user_id FROM users WHERE user_id = %s", (user_id,)) is None:
        raise ValidationError("Akun tidak ditemukan.")
    db.execute(
        "UPDATE users SET password_hash = %s WHERE user_id = %s",
        (hash_password(cek_password(password_baru)), user_id),
    )


@require_role(ADMIN)
def set_aktif(user_id, aktif):
    user_id = cek_id(user_id, "Akun")
    if user_id == session.get_user()["user_id"] and not aktif:
        raise ValidationError("Anda tidak dapat menonaktifkan akun Anda sendiri.")
    if db.fetch_one("SELECT user_id FROM users WHERE user_id = %s", (user_id,)) is None:
        raise ValidationError("Akun tidak ditemukan.")
    db.execute("UPDATE users SET is_active = %s WHERE user_id = %s", (1 if aktif else 0, user_id))


def ganti_password(password_lama, password_baru):
    """Mengganti password akun yang sedang login (admin maupun mahasiswa)."""
    if not session.is_logged_in():
        raise AuthError("Sesi tidak aktif. Silakan login kembali.")
    user_id = session.get_user()["user_id"]
    baris = db.fetch_one("SELECT password_hash FROM users WHERE user_id = %s", (user_id,))
    if baris is None or not verify_password(password_lama or "", baris["password_hash"]):
        raise AuthError("Password lama salah.")
    db.execute(
        "UPDATE users SET password_hash = %s WHERE user_id = %s",
        (hash_password(cek_password(password_baru)), user_id),
    )