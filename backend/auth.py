"""Autentikasi dan registrasi akun berdasarkan tabel users/roles."""
from datetime import datetime, timedelta

from config import SESSION_TIMEOUT_MINUTES
from database import connection as db
from utils import session
from utils.permissions import ADMIN, DOSEN, require_role
from utils.security import dummy_verify, hash_password, verify_password
from utils.validators import (
    AuthError,
    ValidationError,
    cek_angkatan,
    cek_id,
    cek_nama_orang,
    cek_nim,
    cek_password,
    cek_tanggal,
    cek_wajib,
)

PESAN_GAGAL_LOGIN = "Username/NIM atau password salah."


def _mulai_sesi(**data):
    data["expires_at"] = datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    session.set_user(data)
    return data


def login(username, password):
    """Login admin, dosen, atau mahasiswa dari tabel users dan roles."""
    username = (username or "").strip()
    if not username or not password:
        raise AuthError("Username/NIM dan password wajib diisi.")
    user = db.fetch_one(
        "SELECT u.user_id, u.username, u.password_hash, u.is_active, r.nama_role "
        "FROM users u JOIN roles r ON r.role_id = u.role_id WHERE u.username = %s",
        (username,),
    )
    if user is None:
        dummy_verify(password)
        raise AuthError(PESAN_GAGAL_LOGIN)
    if not verify_password(password, user["password_hash"]):
        raise AuthError(PESAN_GAGAL_LOGIN)
    if not user["is_active"]:
        raise AuthError("Akun dinonaktifkan.")

    role = user["nama_role"]
    profile = None
    dosen_id = None
    if role == "mahasiswa":
        profile = db.fetch_one(
            "SELECT mahasiswa_id, nim, nama_lengkap, status_mahasiswa "
            "FROM mahasiswa WHERE user_id = %s",
            (user["user_id"],),
        )
        if profile is None:
            raise AuthError("Profil mahasiswa tidak ditemukan. Hubungi admin.")
        if profile["status_mahasiswa"] in ("DO", "Keluar"):
            raise AuthError(f"Akun tidak dapat digunakan (status: {profile['status_mahasiswa']}).")
    elif role == "dosen":
        profile = db.fetch_one(
            "SELECT dosen_id, nama_lengkap, status FROM dosen WHERE user_id = %s",
            (user["user_id"],),
        )
        if profile is None:
            raise AuthError("Profil dosen tidak ditemukan. Hubungi admin.")
        if profile["status"] in ("Pensiun", "Keluar"):
            raise AuthError("Akun dosen tidak aktif.")
        dosen_id = profile["dosen_id"]
    elif role != "admin":
        raise AuthError("Role ini belum dapat login ke aplikasi.")

    db.execute(
        "UPDATE users SET last_login_at = %s WHERE user_id = %s",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["user_id"]),
    )
    return _mulai_sesi(
        role=role,
        user_id=user["user_id"],
        username=user["username"],
        nama=profile["nama_lengkap"] if profile else user["username"],
        nim=profile.get("nim") if role == "mahasiswa" else None,
        mahasiswa_id=profile.get("mahasiswa_id") if role == "mahasiswa" else None,
        dosen_id=dosen_id,
        admin_id=user["user_id"] if role == "admin" else None,
    )


def login_mahasiswa(nim, password):
    user = login(nim, password)
    if user["role"] != "mahasiswa":
        logout()
        raise AuthError(PESAN_GAGAL_LOGIN)
    return user


def login_admin(username, password):
    user = login(username, password)
    if user["role"] != "admin":
        logout()
        raise AuthError(PESAN_GAGAL_LOGIN)
    return user


def logout():
    session.clear()


def pengguna_saat_ini():
    return session.get_user() if session.is_logged_in() else None


@require_role(ADMIN, DOSEN)
def daftar_jurusan():
    return db.fetch_all(
        "SELECT jurusan_id, kode_jurusan, nama_jurusan FROM jurusan ORDER BY nama_jurusan"
    )


@require_role(ADMIN, DOSEN)
def daftar_prodi(jurusan_id):
    jurusan_id = cek_id(jurusan_id, "Jurusan")
    return db.fetch_all(
        "SELECT prodi_id, jurusan_id, kode_prodi, nama_prodi, jenjang "
        "FROM program_studi WHERE jurusan_id = %s ORDER BY nama_prodi",
        (jurusan_id,),
    )


@require_role(ADMIN)
def daftar_dosen(prodi_id):
    prodi_id = cek_id(prodi_id, "Program studi")
    return db.fetch_all(
        "SELECT dosen_id, nama_lengkap, nidn, nip FROM dosen "
        "WHERE prodi_id = %s AND status = 'Aktif' ORDER BY nama_lengkap",
        (prodi_id,),
    )


@require_role(ADMIN)
def registrasi(
    username, email, password, nim, nama, prodi_id, dosen_pa_id,
    jenis_kelamin, tanggal_lahir, angkatan, tempat_lahir=None, agama=None,
    nik=None, alamat=None, no_hp=None, nama_ayah=None, nama_ibu=None,
):
    """Buat user dan profil mahasiswa dalam satu transaksi."""
    username = cek_nim(username)
    nim = cek_nim(nim)
    if username != nim:
        raise ValidationError("Username mahasiswa harus sama dengan NIM.")
    email = cek_wajib(email, "Email").strip()
    if "@" not in email or len(email) > 100:
        raise ValidationError("Email tidak valid.")
    password = cek_password(password)
    nama = cek_nama_orang(nama, "Nama")
    prodi_id = cek_id(prodi_id, "Program studi")
    dosen_pa_id = cek_id(dosen_pa_id, "Dosen PA")
    jenis_kelamin = (jenis_kelamin or "").strip().upper()
    if jenis_kelamin not in ("L", "P"):
        raise ValidationError("Jenis kelamin harus L atau P.")
    tanggal_lahir = cek_tanggal(tanggal_lahir, "Tanggal lahir")
    angkatan = cek_angkatan(angkatan)
    for label, value, limit in (
        ("Tempat lahir", tempat_lahir, 50), ("Agama", agama, 20),
        ("Nomor HP", no_hp, 20), ("Nama ayah", nama_ayah, 100),
        ("Nama ibu", nama_ibu, 100),
    ):
        if value is not None and len(str(value).strip()) > limit:
            raise ValidationError(f"{label} maksimal {limit} karakter.")
    if nik is not None:
        nik = str(nik).strip() or None
        if nik is not None and (len(nik) != 16 or not nik.isdigit()):
            raise ValidationError("NIK harus terdiri dari 16 angka.")
    if db.fetch_one("SELECT prodi_id FROM program_studi WHERE prodi_id = %s", (prodi_id,)) is None:
        raise ValidationError("Program studi tidak ditemukan.")
    if db.fetch_one(
        "SELECT dosen_id FROM dosen WHERE dosen_id = %s AND prodi_id = %s AND status = 'Aktif'",
        (dosen_pa_id, prodi_id),
    ) is None:
        raise ValidationError("Dosen PA harus dosen aktif dari program studi yang dipilih.")

    with db.db_cursor(commit=True) as cur:
        cur.execute("SELECT role_id FROM roles WHERE nama_role = %s", ("mahasiswa",))
        role = cur.fetchone()
        if role is None:
            raise ValidationError("Role mahasiswa belum tersedia. Jalankan database/seed.sql.")
        cur.execute(
            "INSERT INTO users (role_id, username, email, password_hash, is_active) "
            "VALUES (%s, %s, %s, %s, TRUE)",
            (role["role_id"], username, email, hash_password(password)),
        )
        user_id = cur.lastrowid
        cur.execute(
            "INSERT INTO mahasiswa (user_id, prodi_id, dosen_pa_id, nim, nama_lengkap, "
            "jenis_kelamin, tempat_lahir, tanggal_lahir, agama, nik, alamat, no_hp, "
            "nama_ayah, nama_ibu, angkatan, status_mahasiswa) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Aktif')",
            (user_id, prodi_id, dosen_pa_id, nim, nama, jenis_kelamin, tempat_lahir,
             tanggal_lahir, agama, nik, alamat, no_hp, nama_ayah, nama_ibu, angkatan),
        )
    return nim


register = registrasi
