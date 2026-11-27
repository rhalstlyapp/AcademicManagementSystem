"""Menyimpan user yang sedang login (satu pengguna per aplikasi desktop)."""
from datetime import datetime

_current_user = None


def set_user(user: dict) -> None:
    global _current_user
    _current_user = user


def get_user():
    return _current_user


def clear() -> None:
    global _current_user
    _current_user = None


def is_logged_in() -> bool:
    return _current_user is not None and not is_expired()


def is_expired() -> bool:
    if _current_user is None:
        return True
    return datetime.now() >= _current_user["expires_at"]


def get_role():
    return _current_user["role"] if _current_user else None


def has_role(*roles) -> bool:
    return is_logged_in() and _current_user["role"] in roles