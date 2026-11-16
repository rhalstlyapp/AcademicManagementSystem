"""Login dan logout."""
import hashlib
import secrets
from datetime import datetime, timedelta

from backend import log
from config import SESSION_TIMEOUT_MINUTES
from database.connection import execute, fetch_one
from utils import session
from utils.security import dummy_verify, verify_password

PESAN_GAGAL = "Username atau password salah."


class AuthError(Exception):
    """Error login yang pesannya aman ditampilkan ke pengguna."""


_SQL_USER = """
    SELECT u.user_id, u.username, u.email, u.password_hash, u.is_active,
           r.nama_role AS role,
           d.dosen_id, m.mahasiswa_id,
           COALESCE(d.nama_lengkap, m.nama_lengkap, u.username) AS nama
    FROM users u
    JOIN roles r ON r.role_id = u.role_id
    LEFT JOIN dosen d ON d.user_id = u.user_id
    LEFT JOIN mahasiswa m ON m.user_id = u.user_id
    WHERE u.username = %s
"""


def login(username: str, password: str) -> dict:
    username = (username or "").strip()
    if not username or not password:
        raise AuthError("Username dan password wajib diisi.")

    user = fetch_one(_SQL_USER, (username,))

    if user is None:
        dummy_verify(password)
        log.catat(None, "LOGIN_GAGAL", "auth", detail={"username": username})
        raise AuthError(PESAN_GAGAL)

    if not verify_password(password, user["password_hash"]):
        log.catat(user["user_id"], "LOGIN_GAGAL", "auth")
        raise AuthError(PESAN_GAGAL)

    if not user["is_active"]:
        log.catat(user["user_id"], "LOGIN_DITOLAK", "auth", detail={"alasan": "akun nonaktif"})
        raise AuthError("Akun dinonaktifkan. Hubungi admin.")

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    session_id = log.buat_session(user["user_id"], token_hash, expires_at)
    execute("UPDATE users SET last_login_at = NOW() WHERE user_id = %s", (user["user_id"],))
    log.catat(user["user_id"], "LOGIN", "auth")

    current = {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "nama": user["nama"],
        "dosen_id": user["dosen_id"],
        "mahasiswa_id": user["mahasiswa_id"],
        "session_id": session_id,
        "expires_at": expires_at,
    }
    session.set_user(current)
    return current


def logout() -> None:
    user = session.get_user()
    if user is not None:
        log.tutup_session(user["session_id"])
        log.catat(user["user_id"], "LOGOUT", "auth")
    session.clear()