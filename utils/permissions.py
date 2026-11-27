"""Hak akses berbasis role: admin, dosen, dan mahasiswa."""
from functools import wraps

from utils import session
from utils.validators import AksesDitolak

ADMIN = "admin"
DOSEN = "dosen"
MAHASISWA = "mahasiswa"
SEMUA = (ADMIN, DOSEN, MAHASISWA)

# Menu/halaman -> role yang boleh membuka.
MENU_ACCESS = {
    "dashboard":       SEMUA,
    "agenda_tugas":    (MAHASISWA,),
    "nilai":           (ADMIN, DOSEN),
    "transkrip":       (ADMIN, DOSEN, MAHASISWA),
    "dosen":           (ADMIN,),
    "kelas":           (ADMIN,),
    "mahasiswa":       (ADMIN, DOSEN),
    "akademik_master": (ADMIN,),
    "profil": (ADMIN, DOSEN, MAHASISWA),
}


def can_access(menu: str) -> bool:
    return session.has_role(*MENU_ACCESS.get(menu, ()))


def menus_for_current_user():
    return [menu for menu in MENU_ACCESS if can_access(menu)]


def require_role(*roles):
    """Dekorator untuk fungsi backend:

        @require_role(ADMIN)
        def hapus(...): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not session.is_logged_in():
                raise AksesDitolak("Sesi tidak aktif. Silakan login kembali.")
            if not session.has_role(*roles):
                raise AksesDitolak("Anda tidak memiliki akses untuk tindakan ini.")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def efektif_nim(nim=None):
    """Menentukan data mahasiswa mana yang boleh dilihat pengguna saat ini.

    Admin: bebas (mengembalikan nilai yang diminta, bisa None).
    Mahasiswa: hanya NIM miliknya sendiri; meminta data orang lain ditolak.
    """
    if not session.is_logged_in():
        raise AksesDitolak("Sesi tidak aktif. Silakan login kembali.")
    pengguna = session.get_user()
    if pengguna["role"] in (ADMIN, DOSEN):
        return nim
    if pengguna["role"] != MAHASISWA:
        raise AksesDitolak("Role tidak dapat melihat data nilai.")
    milik_sendiri = pengguna["nim"]
    if nim is not None and str(nim).strip().casefold() != milik_sendiri.casefold():
        raise AksesDitolak("Anda hanya dapat melihat data milik sendiri.")
    return milik_sendiri


def efektif_mahasiswa_id(mahasiswa_id=None):
    """Mahasiswa hanya dapat melihat profilnya; admin/dosen boleh memilih profil."""
    if not session.is_logged_in():
        raise AksesDitolak("Sesi tidak aktif. Silakan login kembali.")
    pengguna = session.get_user()
    if pengguna["role"] in (ADMIN, DOSEN):
        return mahasiswa_id
    if pengguna["role"] != MAHASISWA:
        raise AksesDitolak("Role tidak dapat melihat data mahasiswa.")
    milik_sendiri = pengguna.get("mahasiswa_id")
    if milik_sendiri is None:
        raise AksesDitolak("Profil mahasiswa tidak terhubung ke akun.")
    if mahasiswa_id is not None:
        try:
            id_diminta = int(mahasiswa_id)
        except (TypeError, ValueError):
            raise AksesDitolak("ID mahasiswa tidak valid.") from None
        if id_diminta != int(milik_sendiri):
            raise AksesDitolak("Anda hanya dapat melihat data milik sendiri.")
    return milik_sendiri
