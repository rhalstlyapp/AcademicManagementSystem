"""Login, logout, dan pendaftaran mahasiswa.

Mahasiswa login dengan Nama + NIM (NIM berfungsi sebagai pengganti password).
Admin login dengan username + password (hash bcrypt).
"""
from datetime import datetime, timedelta

from config import SESSION_TIMEOUT_MINUTES
from database import connection as db
from utils import session
from utils.security import dummy_verify, verify_password
from utils.validators import (
    AuthError, ValidationError, cek_id, cek_nama_orang, cek_nim, cek_wajib, normal_nama,
)

PESAN_GAGAL_MAHASISWA = "Nama atau NIM salah."
PESAN_GAGAL_ADMIN = "Username atau password salah."
STATUS_DITOLAK = ("DO", "Keluar")


def _stempel(waktu):
    return waktu.strftime("%Y-%m-%d %H:%M:%S")


def _mulai_sesi(**data):
    data["expires_at"] = datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    session.set_user(data)
    return data


# ---------------------------------------------------------------- login
def login_mahasiswa(nama, nim):
    """Nama dan NIM harus cocok. Nama tidak peka huruf besar/kecil dan spasi berlebih."""
    nama = (nama or "").strip()
    nim = (nim or "").strip()
    if not nama or not nim:
        raise AuthError("Nama dan NIM wajib diisi.")

    baris = db.fetch_one(
        "SELECT nim, nama_lengkap, status_mahasiswa FROM mahasiswa WHERE nim = %s", (nim,)
    )
    if baris is None or normal_nama(baris["nama_lengkap"]) != normal_nama(nama):
        raise AuthError(PESAN_GAGAL_MAHASISWA)
    if baris["status_mahasiswa"] in STATUS_DITOLAK:
        raise AuthError(
            f"Akun tidak dapat digunakan (status: {baris['status_mahasiswa']}). Hubungi admin."
        )

    return _mulai_sesi(
        role="mahasiswa",
        nim=baris["nim"],
        nama=baris["nama_lengkap"],
        username=baris["nim"],
        admin_id=None,
    )


def login_admin(username, password):
    username = (username or "").strip()
    if not username or not password:
        raise AuthError("Username dan password wajib diisi.")

    baris = db.fetch_one(
        "SELECT admin_id, username, password_hash, is_active FROM admin WHERE username = %s",
        (username,),
    )
    if baris is None:
        dummy_verify(password)          # samakan waktu respons dengan username yang ada
        raise AuthError(PESAN_GAGAL_ADMIN)
    if not verify_password(password, baris["password_hash"]):
        raise AuthError(PESAN_GAGAL_ADMIN)
    if not baris["is_active"]:
        raise AuthError("Akun dinonaktifkan.")

    db.execute(
        "UPDATE admin SET last_login_at = %s WHERE admin_id = %s",
        (_stempel(datetime.now()), baris["admin_id"]),
    )
    return _mulai_sesi(
        role="admin",
        nim=None,
        nama=baris["username"],
        username=baris["username"],
        admin_id=baris["admin_id"],
    )


def logout():
    session.clear()


def pengguna_saat_ini():
    return session.get_user()


# ------------------------------------------------- data publik untuk formulir daftar
def daftar_jurusan():
    """Dipakai dropdown pada formulir pendaftaran (pengguna belum login)."""
    return db.fetch_all(
        "SELECT jurusan_id, kode_jurusan, nama_jurusan FROM jurusan ORDER BY nama_jurusan"
    )


def daftar_prodi(jurusan_id):
    """Prodi di bawah satu jurusan, untuk dropdown yang bergantung pada jurusan."""
    jurusan_id = cek_id(jurusan_id, "Jurusan")
    return db.fetch_all(
        "SELECT prodi_id, kode_prodi, nama_prodi, jenjang FROM program_studi "
        "WHERE jurusan_id = %s ORDER BY nama_prodi",
        (jurusan_id,),
    )


# ------------------------------------------------------------ pendaftaran
def registrasi(nama, nim, prodi_id):
    """Mendaftarkan mahasiswa baru (status Aktif). Mengembalikan NIM.
    Jurusan tidak disimpan; ia diturunkan dari prodi."""
    nama = cek_nama_orang(nama, "Nama")
    nim = cek_nim(nim)
    prodi_id = cek_id(cek_wajib(prodi_id, "Program studi"), "Program studi")

    if db.fetch_one("SELECT prodi_id FROM program_studi WHERE prodi_id = %s", (prodi_id,)) is None:
        raise ValidationError("Program studi tidak ditemukan.")
    if db.fetch_one("SELECT nim FROM mahasiswa WHERE nim = %s", (nim,)):
        raise ValidationError("NIM sudah terdaftar.")

    db.execute(
        "INSERT INTO mahasiswa (nim, prodi_id, nama_lengkap, status_mahasiswa) "
        "VALUES (%s, %s, %s, 'Aktif')",
        (nim, prodi_id, nama),
    )
    return nim