"""Login, logout, dan pendaftaran akun.

Struktur autentikasi menggunakan tabel users + roles.

Mahasiswa:
    Login menggunakan Nama + NIM.

Dosen/Admin:
    Login menggunakan username + password.

Mahasiswa yang melakukan registrasi publik belum memiliki password.
"""

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


# ==============================================================
# Session
# ==============================================================

def _mulai_sesi(**data):
    """Menyimpan data pengguna ke session dengan waktu kedaluwarsa."""

    data["expires_at"] = datetime.now() + timedelta(
        minutes=SESSION_TIMEOUT_MINUTES
    )

    session.set_user(data)

    return data


def logout():
    """Menghapus session pengguna."""

    session.clear()


def pengguna_saat_ini():
    """Mengembalikan pengguna yang sedang login."""

    return session.get_user() if session.is_logged_in() else None


# ==============================================================
# Login umum
# ==============================================================

def login(username, password):
    """Login akun berpassword dari tabel users/roles.

    Digunakan untuk Admin dan Dosen.
    """

    username = (username or "").strip()

    if not username or not password:
        raise AuthError(
            "Username/NIM dan password wajib diisi."
        )

    user = db.fetch_one(
        """
        SELECT
            u.user_id,
            u.username,
            u.password_hash,
            u.is_active,
            r.nama_role
        FROM users u
        JOIN roles r
            ON r.role_id = u.role_id
        WHERE u.username = %s
        """,
        (username,),
    )

    # Tetap lakukan dummy bcrypt verification
    # agar waktu respons username tidak ditemukan
    # tidak terlalu berbeda dengan username yang ditemukan.
    if user is None:
        dummy_verify(password)
        raise AuthError(PESAN_GAGAL_LOGIN)

    if (
        not user["password_hash"]
        or not verify_password(
            password,
            user["password_hash"],
        )
    ):
        raise AuthError(PESAN_GAGAL_LOGIN)

    if not user["is_active"]:
        raise AuthError("Akun dinonaktifkan.")

    role = user["nama_role"]

    profile = None
    dosen_id = None

    # ----------------------------------------------------------
    # Profil mahasiswa
    # ----------------------------------------------------------

    if role == "mahasiswa":
        profile = db.fetch_one(
            """
            SELECT
                mahasiswa_id,
                nim,
                nama_lengkap,
                status_mahasiswa
            FROM mahasiswa
            WHERE user_id = %s
            """,
            (user["user_id"],),
        )

        if profile is None:
            raise AuthError(
                "Profil mahasiswa tidak ditemukan. Hubungi admin."
            )

        if profile["status_mahasiswa"] in (
            "DO",
            "Keluar",
        ):
            raise AuthError(
                f"Akun tidak dapat digunakan "
                f"(status: {profile['status_mahasiswa']})."
            )

    # ----------------------------------------------------------
    # Profil dosen
    # ----------------------------------------------------------

    elif role == "dosen":
        profile = db.fetch_one(
            """
            SELECT
                dosen_id,
                nama_lengkap,
                status
            FROM dosen
            WHERE user_id = %s
            """,
            (user["user_id"],),
        )

        if profile is None:
            raise AuthError(
                "Profil dosen tidak ditemukan. Hubungi admin."
            )

        if profile["status"] in (
            "Pensiun",
            "Keluar",
        ):
            raise AuthError(
                "Akun dosen tidak aktif."
            )

        dosen_id = profile["dosen_id"]

    # ----------------------------------------------------------
    # Role lain
    # ----------------------------------------------------------

    elif role != "admin":
        raise AuthError(
            "Role ini belum dapat login ke aplikasi."
        )

    # ----------------------------------------------------------
    # Update waktu login
    # ----------------------------------------------------------

    db.execute(
        """
        UPDATE users
        SET last_login_at = %s
        WHERE user_id = %s
        """,
        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            user["user_id"],
        ),
    )

    return _mulai_sesi(
        role=role,
        user_id=user["user_id"],
        username=user["username"],
        nama=(
            profile["nama_lengkap"]
            if profile
            else user["username"]
        ),
        nim=(
            profile["nim"]
            if role == "mahasiswa"
            else None
        ),
        mahasiswa_id=(
            profile["mahasiswa_id"]
            if role == "mahasiswa"
            else None
        ),
        dosen_id=dosen_id,
        admin_id=(
            user["user_id"]
            if role == "admin"
            else None
        ),
    )


# ==============================================================
# Login mahasiswa
# ==============================================================

def login_mahasiswa(nama, nim):
    """Login mahasiswa menggunakan Nama + NIM."""

    nama = cek_nama_orang(
        nama,
        "Nama",
    )

    nim = cek_nim(nim)

    user = db.fetch_one(
        """
        SELECT
            u.user_id,
            u.username,
            u.is_active,
            m.mahasiswa_id,
            m.nim,
            m.nama_lengkap,
            m.status_mahasiswa
        FROM users u
        JOIN roles r
            ON r.role_id = u.role_id
        JOIN mahasiswa m
            ON m.user_id = u.user_id
        WHERE
            r.nama_role = 'mahasiswa'
            AND u.username = %s
            AND m.nim = %s
            AND LOWER(TRIM(m.nama_lengkap))
                = LOWER(TRIM(%s))
        """,
        (
            nim,
            nim,
            nama,
        ),
    )

    if user is None or not user["is_active"]:
        raise AuthError(
            PESAN_GAGAL_LOGIN
        )

    if user["status_mahasiswa"] in (
        "DO",
        "Keluar",
    ):
        raise AuthError(
            f"Akun tidak dapat digunakan "
            f"(status: {user['status_mahasiswa']})."
        )

    db.execute(
        """
        UPDATE users
        SET last_login_at = %s
        WHERE user_id = %s
        """,
        (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            user["user_id"],
        ),
    )

    return _mulai_sesi(
        role="mahasiswa",
        user_id=user["user_id"],
        username=user["username"],
        nama=user["nama_lengkap"],
        nim=user["nim"],
        mahasiswa_id=user["mahasiswa_id"],
        dosen_id=None,
        admin_id=None,
    )


# ==============================================================
# Login khusus berdasarkan role
# ==============================================================

def login_admin(username, password):
    """Login khusus Admin."""

    user = login(
        username,
        password,
    )

    if user["role"] != ADMIN:
        logout()
        raise AuthError(
            PESAN_GAGAL_LOGIN
        )

    return user


def login_dosen(username, password):
    """Login khusus Dosen."""

    user = login(
        username,
        password,
    )

    if user["role"] != DOSEN:
        logout()
        raise AuthError(
            PESAN_GAGAL_LOGIN
        )

    return user


# ==============================================================
# Data untuk form registrasi
# ==============================================================

def daftar_jurusan():
    """Data jurusan untuk dropdown registrasi."""

    return db.fetch_all(
        """
        SELECT
            jurusan_id,
            kode_jurusan,
            nama_jurusan
        FROM jurusan
        ORDER BY nama_jurusan
        """
    )


def daftar_prodi(jurusan_id):
    """Data program studi berdasarkan jurusan."""

    jurusan_id = cek_id(
        jurusan_id,
        "Jurusan",
    )

    return db.fetch_all(
        """
        SELECT
            prodi_id,
            jurusan_id,
            kode_prodi,
            nama_prodi,
            jenjang
        FROM program_studi
        WHERE jurusan_id = %s
        ORDER BY jenjang, nama_prodi
        """,
        (jurusan_id,),
    )


def daftar_dosen(prodi_id):
    """Data dosen aktif berdasarkan program studi."""

    prodi_id = cek_id(
        prodi_id,
        "Program studi",
    )

    return db.fetch_all(
        """
        SELECT
            dosen_id,
            nama_lengkap,
            nidn,
            nip
        FROM dosen
        WHERE
            prodi_id = %s
            AND status = 'Aktif'
        ORDER BY nama_lengkap
        """,
        (prodi_id,),
    )


def opsi_prodi_registrasi():
    """Data program studi untuk formulir pendaftaran publik."""

    return db.fetch_all(
        """
        SELECT
            prodi_id,
            kode_prodi,
            nama_prodi,
            jenjang
        FROM program_studi
        WHERE jenjang IN ('D3', 'D4')
        ORDER BY jenjang, nama_prodi
        """
    )


def opsi_dosen_pa(prodi_id):
    """Dosen PA aktif pada program studi tertentu."""

    prodi_id = cek_id(
        prodi_id,
        "Program studi",
    )

    return db.fetch_all(
        """
        SELECT
            dosen_id,
            nama_lengkap
        FROM dosen
        WHERE
            prodi_id = %s
            AND status = 'Aktif'
        ORDER BY nama_lengkap
        """,
        (prodi_id,),
    )


# ==============================================================
# Registrasi mahasiswa oleh Admin
# ==============================================================

@require_role(ADMIN)
def registrasi(
    username,
    email,
    password,
    nim,
    nama,
    prodi_id,
    dosen_pa_id,
    jenis_kelamin,
    tanggal_lahir,
    angkatan,
    tempat_lahir=None,
    agama=None,
    nik=None,
    alamat=None,
    no_hp=None,
    nama_ayah=None,
    nama_ibu=None,
):
    """Admin membuat akun mahasiswa dengan profil lengkap."""

    username = cek_nim(username)
    nim = cek_nim(nim)

    if username != nim:
        raise ValidationError(
            "Username mahasiswa harus sama dengan NIM."
        )

    email = cek_wajib(
        email,
        "Email",
    ).strip()

    if "@" not in email or len(email) > 100:
        raise ValidationError(
            "Email tidak valid."
        )

    password = cek_password(
        password
    )

    nama = cek_nama_orang(
        nama,
        "Nama",
    )

    prodi_id = cek_id(
        prodi_id,
        "Program studi",
    )

    dosen_pa_id = cek_id(
        dosen_pa_id,
        "Dosen PA",
    )

    jenis_kelamin = (
        jenis_kelamin or ""
    ).strip().upper()

    if jenis_kelamin not in (
        "L",
        "P",
    ):
        raise ValidationError(
            "Jenis kelamin harus L atau P."
        )

    tanggal_lahir = cek_tanggal(
        tanggal_lahir,
        "Tanggal lahir",
    )

    angkatan = cek_angkatan(
        angkatan
    )

    for label, value, limit in (
        (
            "Tempat lahir",
            tempat_lahir,
            50,
        ),
        (
            "Agama",
            agama,
            20,
        ),
        (
            "Nomor HP",
            no_hp,
            20,
        ),
        (
            "Nama ayah",
            nama_ayah,
            100,
        ),
        (
            "Nama ibu",
            nama_ibu,
            100,
        ),
    ):
        if (
            value is not None
            and len(str(value).strip()) > limit
        ):
            raise ValidationError(
                f"{label} maksimal {limit} karakter."
            )

    if nik is not None:
        nik = str(nik).strip() or None

        if (
            nik is not None
            and (
                len(nik) != 16
                or not nik.isdigit()
            )
        ):
            raise ValidationError(
                "NIK harus terdiri dari 16 angka."
            )

    # ----------------------------------------------------------
    # Pastikan prodi ada
    # ----------------------------------------------------------

    if db.fetch_one(
        """
        SELECT prodi_id
        FROM program_studi
        WHERE prodi_id = %s
        """,
        (prodi_id,),
    ) is None:
        raise ValidationError(
            "Program studi tidak ditemukan."
        )

    # ----------------------------------------------------------
    # Pastikan dosen PA sesuai prodi dan aktif
    # ----------------------------------------------------------

    if db.fetch_one(
        """
        SELECT dosen_id
        FROM dosen
        WHERE
            dosen_id = %s
            AND prodi_id = %s
            AND status = 'Aktif'
        """,
        (
            dosen_pa_id,
            prodi_id,
        ),
    ) is None:
        raise ValidationError(
            "Dosen PA harus dosen aktif dari program studi yang dipilih."
        )

    # ----------------------------------------------------------
    # Insert users + mahasiswa dalam satu transaksi
    # ----------------------------------------------------------

    with db.db_cursor(commit=True) as cur:

        cur.execute(
            """
            SELECT role_id
            FROM roles
            WHERE nama_role = %s
            """,
            ("mahasiswa",),
        )

        role = cur.fetchone()

        if role is None:
            raise ValidationError(
                "Role mahasiswa belum tersedia. "
                "Jalankan database/seed.sql."
            )

        cur.execute(
            """
            INSERT INTO users (
                role_id,
                username,
                email,
                password_hash,
                is_active
            )
            VALUES (%s, %s, %s, %s, TRUE)
            """,
            (
                role["role_id"],
                username,
                email,
                hash_password(password),
            ),
        )

        user_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO mahasiswa (
                user_id,
                prodi_id,
                dosen_pa_id,
                nim,
                nama_lengkap,
                jenis_kelamin,
                tempat_lahir,
                tanggal_lahir,
                agama,
                nik,
                alamat,
                no_hp,
                nama_ayah,
                nama_ibu,
                angkatan,
                status_mahasiswa
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                'Aktif'
            )
            """,
            (
                user_id,
                prodi_id,
                dosen_pa_id,
                nim,
                nama,
                jenis_kelamin,
                tempat_lahir,
                tanggal_lahir,
                agama,
                nik,
                alamat,
                no_hp,
                nama_ayah,
                nama_ibu,
                angkatan,
            ),
        )

    return nim


# ==============================================================
# Registrasi mahasiswa publik
# ==============================================================

def registrasi_mahasiswa(
    nama,
    nim,
    prodi_id,
):
    """Pendaftaran mandiri mahasiswa dari halaman Login.

    Akun dibuat tanpa password karena login mahasiswa
    menggunakan Nama + NIM.
    """

    nama = cek_nama_orang(
        nama,
        "Nama",
    )

    nim = cek_nim(
        nim
    )

    prodi_id = cek_id(
        prodi_id,
        "Program studi",
    )

    if db.fetch_one(
        """
        SELECT prodi_id
        FROM program_studi
        WHERE prodi_id = %s
        """,
        (prodi_id,),
    ) is None:
        raise ValidationError(
            "Program studi tidak ditemukan."
        )

    if db.fetch_one(
        """
        SELECT mahasiswa_id
        FROM mahasiswa
        WHERE nim = %s
        """,
        (nim,),
    ):
        raise ValidationError(
            "NIM sudah terdaftar."
        )

    with db.db_cursor(commit=True) as cur:

        cur.execute(
            """
            SELECT role_id
            FROM roles
            WHERE nama_role = %s
            """,
            ("mahasiswa",),
        )

        role = cur.fetchone()

        if role is None:
            raise ValidationError(
                "Role mahasiswa belum tersedia. "
                "Jalankan database/seed.sql."
            )

        cur.execute(
            """
            INSERT INTO users (
                role_id,
                username,
                email,
                password_hash,
                is_active
            )
            VALUES (%s, %s, NULL, NULL, TRUE)
            """,
            (
                role["role_id"],
                nim,
            ),
        )

        user_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO mahasiswa (
                user_id,
                prodi_id,
                dosen_pa_id,
                nim,
                nama_lengkap,
                jenis_kelamin,
                tanggal_lahir,
                angkatan,
                status_mahasiswa
            )
            VALUES (
                %s, %s, NULL, %s, %s,
                NULL, NULL, NULL, 'Aktif'
            )
            """,
            (
                user_id,
                prodi_id,
                nim,
                nama,
            ),
        )

    return nim