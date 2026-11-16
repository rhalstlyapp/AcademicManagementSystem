"""Hak akses berbasis role (Admin, Dosen, Mahasiswa)."""
from functools import wraps

from utils import session

ADMIN = "admin"
DOSEN = "dosen"
MAHASISWA = "mahasiswa"
SEMUA = (ADMIN, DOSEN, MAHASISWA)

# Menu/halaman -> role yang boleh membuka. Sesuaikan bila aturan berubah.
MENU_ACCESS = {
    "dashboard":       SEMUA,
    "user":            (ADMIN,),
    "akademik_master": (ADMIN,),
    "dosen":           (ADMIN,),
    "mahasiswa":       (ADMIN, DOSEN),
    "perkuliahan":     SEMUA,
    "krs":             SEMUA,
    "nilai":           SEMUA,
    "transkrip":       SEMUA,
}


def can_access(menu: str) -> bool:
    return session.has_role(*MENU_ACCESS.get(menu, ()))


def menus_for_current_user():
    return [m for m in MENU_ACCESS if can_access(m)]


def require_role(*roles):
    """Dekorator untuk fungsi backend:

        @require_role(ADMIN)
        def hapus_user(user_id): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not session.has_role(*roles):
                raise PermissionError("Anda tidak memiliki akses untuk tindakan ini.")
            return func(*args, **kwargs)
        return wrapper
    return decorator