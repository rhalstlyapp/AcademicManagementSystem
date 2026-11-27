"""Simpan rekomendasi akun lokal dengan enkripsi Windows DPAPI."""
import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


_MAX_AKUN = 5
_CRYPTPROTECT_UI_FORBIDDEN = 0x1


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


def _lokasi_file(nama_file="recent_students.dat"):
    local_app_data = os.getenv("LOCALAPPDATA")
    if os.name != "nt" or not local_app_data:
        return None
    return Path(local_app_data) / "AcademicManagementSystem" / nama_file


def _dpapi(data, lindungi):
    """Enkripsi/dekripsi dengan Windows DPAPI untuk akun Windows saat ini."""
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    input_buffer = ctypes.create_string_buffer(data)
    input_blob = _DataBlob(
        len(data), ctypes.cast(input_buffer, ctypes.POINTER(ctypes.c_byte))
    )
    output_blob = _DataBlob()
    flags = _CRYPTPROTECT_UI_FORBIDDEN

    if lindungi:
        fungsi = crypt32.CryptProtectData
        fungsi.argtypes = [
            ctypes.POINTER(_DataBlob), wintypes.LPCWSTR,
            ctypes.POINTER(_DataBlob), wintypes.LPVOID, wintypes.LPVOID,
            wintypes.DWORD, ctypes.POINTER(_DataBlob),
        ]
        fungsi.restype = wintypes.BOOL
        berhasil = fungsi(
            ctypes.byref(input_blob), "SIAKAD akun tersimpan", None,
            None, None, flags, ctypes.byref(output_blob),
        )
    else:
        fungsi = crypt32.CryptUnprotectData
        fungsi.argtypes = [
            ctypes.POINTER(_DataBlob), ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(_DataBlob), wintypes.LPVOID, wintypes.LPVOID,
            wintypes.DWORD, ctypes.POINTER(_DataBlob),
        ]
        fungsi.restype = wintypes.BOOL
        fungsi(
            ctypes.byref(input_blob), None, None, None, None,
            flags, ctypes.byref(output_blob),
        )
        berhasil = bool(output_blob.pbData)

    if not berhasil:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        kernel32.LocalFree(output_blob.pbData)


def muat_akun():
    """Kembalikan daftar akun tersimpan; file tidak tersedia berarti daftar kosong."""
    lokasi = _lokasi_file()
    if lokasi is None or not lokasi.exists():
        return []
    try:
        isi = json.loads(_dpapi(lokasi.read_bytes(), lindungi=False).decode("utf-8"))
        return [
            akun for akun in isi
            if isinstance(akun, dict)
            and akun.get("nama")
            and str(akun.get("nim", "")).isdigit()
            and len(str(akun["nim"])) == 9
        ][:_MAX_AKUN]
    except (OSError, ValueError, TypeError, ctypes.ArgumentError):
        return []


def simpan_akun(nama, nim):
    """Simpan akun terbaru terenkripsi; hanya dapat dibuka oleh akun Windows ini."""
    lokasi = _lokasi_file()
    nama = " ".join((nama or "").split())
    nim = str(nim or "").strip()
    if lokasi is None or not nama or not nim.isdigit() or len(nim) != 9:
        return False

    akun = [item for item in muat_akun() if item["nim"] != nim]
    akun.insert(0, {"nama": nama, "nim": nim})
    try:
        lokasi.parent.mkdir(parents=True, exist_ok=True)
        terenkripsi = _dpapi(
            json.dumps(akun[:_MAX_AKUN], ensure_ascii=False).encode("utf-8"),
            lindungi=True,
        )
        lokasi.write_bytes(terenkripsi)
        return True
    except (OSError, ValueError, ctypes.ArgumentError):
        return False


def _muat_username_role(role):
    """Muat daftar username rekomendasi untuk satu role berpassword."""
    if role not in ("admin", "dosen"):
        return []
    nama_file = "recent_admins.dat" if role == "admin" else "recent_dosen.dat"
    lokasi = _lokasi_file(nama_file)
    if lokasi is None or not lokasi.exists():
        return []
    try:
        isi = json.loads(_dpapi(lokasi.read_bytes(), lindungi=False).decode("utf-8"))
        return [
            username for username in isi
            if isinstance(username, str) and 1 <= len(username) <= 50
        ][:_MAX_AKUN]
    except (OSError, ValueError, TypeError, ctypes.ArgumentError):
        return []


def _simpan_username_role(role, username):
    """Simpan maksimal lima username terenkripsi untuk satu role."""
    if role not in ("admin", "dosen"):
        return False
    nama_file = "recent_admins.dat" if role == "admin" else "recent_dosen.dat"
    lokasi = _lokasi_file(nama_file)
    username = " ".join((username or "").split())
    if lokasi is None or not 1 <= len(username) <= 50:
        return False

    akun = [
        item for item in _muat_username_role(role)
        if item.casefold() != username.casefold()
    ]
    akun.insert(0, username)
    try:
        lokasi.parent.mkdir(parents=True, exist_ok=True)
        terenkripsi = _dpapi(
            json.dumps(akun[:_MAX_AKUN], ensure_ascii=False).encode("utf-8"),
            lindungi=True,
        )
        lokasi.write_bytes(terenkripsi)
        return True
    except (OSError, ValueError, ctypes.ArgumentError):
        return False


def _muat_akun_role(role):
    """Muat kredensial terenkripsi untuk satu role berpassword."""
    if role not in ("admin", "dosen"):
        return []
    lokasi = _lokasi_file(f"recent_{role}_credentials.dat")
    if lokasi is None or not lokasi.exists():
        return []
    try:
        isi = json.loads(_dpapi(lokasi.read_bytes(), lindungi=False).decode("utf-8"))
        return [
            akun for akun in isi
            if isinstance(akun, dict)
            and isinstance(akun.get("username"), str)
            and 1 <= len(akun["username"]) <= 50
            and isinstance(akun.get("password"), str)
            and akun["password"]
            and len(akun["password"].encode("utf-8")) <= 72
        ][:_MAX_AKUN]
    except (OSError, ValueError, TypeError, ctypes.ArgumentError):
        return []


def _muat_password_role(role, username):
    """Ambil password tersimpan untuk username dan role yang dipilih."""
    kunci = (username or "").strip().casefold()
    akun = next(
        (item for item in _muat_akun_role(role)
         if item["username"].casefold() == kunci),
        None,
    )
    return akun["password"] if akun else ""


def _simpan_akun_role(role, username, password):
    """Simpan kredensial terenkripsi untuk akun Windows saat ini."""
    if role not in ("admin", "dosen"):
        return False
    lokasi = _lokasi_file(f"recent_{role}_credentials.dat")
    username = " ".join((username or "").split())
    password = password if isinstance(password, str) else ""
    if (
        lokasi is None or not 1 <= len(username) <= 50
        or not password or len(password.encode("utf-8")) > 72
    ):
        return False

    akun = [
        item for item in _muat_akun_role(role)
        if item["username"].casefold() != username.casefold()
    ]
    akun.insert(0, {"username": username, "password": password})
    try:
        lokasi.parent.mkdir(parents=True, exist_ok=True)
        terenkripsi = _dpapi(
            json.dumps(akun[:_MAX_AKUN], ensure_ascii=False).encode("utf-8"),
            lindungi=True,
        )
        lokasi.write_bytes(terenkripsi)
        return True
    except (OSError, ValueError, ctypes.ArgumentError):
        return False

def _hapus_akun_role(role, username):
    """Hapus username dan password tersimpan untuk satu akun."""
    if role not in ("admin", "dosen"):
        return False

    username = (username or "").strip()
    if not username:
        return False

    try:
        # Hapus username dari daftar rekomendasi.
        nama_file = (
            "recent_admins.dat"
            if role == "admin"
            else "recent_dosen.dat"
        )
        lokasi_username = _lokasi_file(nama_file)

        if lokasi_username and lokasi_username.exists():
            daftar = [
                item for item in _muat_username_role(role)
                if item.casefold() != username.casefold()
            ]

            terenkripsi = _dpapi(
                json.dumps(daftar, ensure_ascii=False).encode("utf-8"),
                lindungi=True,
            )
            lokasi_username.write_bytes(terenkripsi)

        # Hapus password dari penyimpanan kredensial.
        lokasi_password = _lokasi_file(
            f"recent_{role}_credentials.dat"
        )

        if lokasi_password and lokasi_password.exists():
            daftar_akun = [
                item for item in _muat_akun_role(role)
                if item["username"].casefold() != username.casefold()
            ]

            if daftar_akun:
                terenkripsi = _dpapi(
                    json.dumps(
                        daftar_akun,
                        ensure_ascii=False,
                    ).encode("utf-8"),
                    lindungi=True,
                )
                lokasi_password.write_bytes(terenkripsi)
            else:
                lokasi_password.unlink()

        return True

    except (OSError, ValueError, TypeError, ctypes.ArgumentError):
        return False


def hapus_akun_admin(username):
    """Hapus akun admin tersimpan."""
    return _hapus_akun_role("admin", username)


def hapus_akun_dosen(username):
    """Hapus akun dosen tersimpan."""
    return _hapus_akun_role("dosen", username)


def muat_username_admin():
    """Muat daftar username admin untuk rekomendasi login."""
    return _muat_username_role("admin")


def simpan_username_admin(username):
    """Simpan maksimal lima username admin terenkripsi."""
    return _simpan_username_role("admin", username)


def muat_akun_admin():
    """Muat username dan password admin yang terenkripsi dengan DPAPI."""
    return _muat_akun_role("admin")


def muat_password_admin(username):
    """Ambil password admin tersimpan untuk username yang dipilih."""
    return _muat_password_role("admin", username)


def simpan_akun_admin(username, password):
    """Simpan kredensial admin terenkripsi untuk akun Windows saat ini."""
    return _simpan_akun_role("admin", username, password)


def muat_username_dosen():
    """Muat daftar username dosen untuk rekomendasi login."""
    return _muat_username_role("dosen")


def simpan_username_dosen(username):
    """Simpan maksimal lima username dosen terenkripsi."""
    return _simpan_username_role("dosen", username)


def muat_akun_dosen():
    """Muat username dan password dosen yang terenkripsi dengan DPAPI."""
    return _muat_akun_role("dosen")


def muat_password_dosen(username):
    """Ambil password dosen tersimpan untuk username yang dipilih."""
    return _muat_password_role("dosen", username)


def simpan_akun_dosen(username, password):
    """Simpan kredensial dosen terenkripsi untuk akun Windows saat ini."""
    return _simpan_akun_role("dosen", username, password)
