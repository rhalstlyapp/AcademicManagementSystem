"""Pencatatan activity_log (aksi pengguna) dan user_sessions (login/logout)."""
import json
import logging

from database.connection import execute

_logger = logging.getLogger(__name__)


def catat(user_id, aksi, modul, record_id=None, detail=None, ip=None):
    """Catat aktivitas. Kegagalan mencatat tidak boleh menggagalkan aksi utama."""
    try:
        execute(
            "INSERT INTO activity_log (user_id, aksi, modul, record_id, detail, ip_address) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                user_id,
                aksi,
                modul,
                None if record_id is None else str(record_id),
                None if detail is None else json.dumps(detail, default=str),
                ip,
            ),
        )
    except Exception:
        _logger.warning("Gagal mencatat activity_log", exc_info=True)


def buat_session(user_id, token_hash, expires_at, ip=None, user_agent=None):
    return execute(
        "INSERT INTO user_sessions (user_id, token_hash, ip_address, user_agent, expires_at) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_id, token_hash, ip, user_agent, expires_at),
    )


def tutup_session(session_id):
    execute(
        "UPDATE user_sessions SET logout_at = NOW() WHERE session_id = %s AND logout_at IS NULL",
        (session_id,),
    )