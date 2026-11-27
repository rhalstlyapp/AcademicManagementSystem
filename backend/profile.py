"""Fitur profil pengguna SIAKAD."""

from datetime import datetime

from database import connection as db
from utils import session
from utils.permissions import ADMIN, DOSEN, MAHASISWA
from utils.security import hash_password, verify_password
from utils.validators import (
    AksesDitolak,
    ValidationError,
    cek_nama_orang,
    cek_nim,
    cek_password,
    cek_teks,
    cek_wajib,
)


# ============================================================
# BANTUAN INTERNAL
# ============================================================

def _pengguna_login():
    pengguna = session.get_user()

    if not pengguna:
        raise AksesDitolak("Anda belum login.")

    return pengguna


def _cek_role(*roles):
    pengguna = _pengguna_login()

    if pengguna.get("role") not in roles:
        raise AksesDitolak("Anda tidak memiliki akses untuk fitur ini.")

    return pengguna


# ============================================================
# PROFIL MAHASISWA
# ============================================================

def profil_mahasiswa():
    pengguna = _cek_role(MAHASISWA)

    mahasiswa_id = pengguna.get("mahasiswa_id")

    if not mahasiswa_id:
        raise ValidationError("Profil mahasiswa tidak ditemukan.")

    data = db.fetch_one(
        """
        SELECT
            m.mahasiswa_id,
            m.user_id,
            m.nim,
            m.nama_lengkap,
            m.jenis_kelamin,
            m.tempat_lahir,
            m.tanggal_lahir,
            m.agama,
            m.nik,
            m.alamat,
            m.no_hp,
            m.nama_ayah,
            m.nama_ibu,
            m.angkatan,
            m.status_mahasiswa,

            p.kode_prodi,
            p.nama_prodi,
            p.jenjang,

            d.nama_lengkap AS nama_dosen_pa

        FROM mahasiswa m

        JOIN program_studi p
            ON p.prodi_id = m.prodi_id

        LEFT JOIN dosen d
            ON d.dosen_id = m.dosen_pa_id

        WHERE m.mahasiswa_id = %s
        """,
        (mahasiswa_id,),
    )

    if data is None:
        raise ValidationError("Data mahasiswa tidak ditemukan.")

    return data


# ============================================================
# PROFIL DOSEN
# ============================================================

def profil_dosen():
    pengguna = _cek_role(DOSEN)

    user_id = pengguna.get("user_id")

    data = db.fetch_one(
        """
        SELECT
            d.dosen_id,
            d.user_id,
            d.nidn,
            d.nip,
            d.nama_lengkap,
            d.jenis_kelamin,
            d.status,

            u.username,
            u.email,

            p.kode_prodi,
            p.nama_prodi,
            p.jenjang

        FROM dosen d

        JOIN users u
            ON u.user_id = d.user_id

        JOIN program_studi p
            ON p.prodi_id = d.prodi_id

        WHERE d.user_id = %s
        """,
        (user_id,),
    )

    if data is None:
        raise ValidationError("Profil dosen tidak ditemukan.")

    return data


# ============================================================
# PROFIL ADMIN
# ============================================================

def profil_admin():
    pengguna = _cek_role(ADMIN)

    user_id = pengguna.get("user_id")

    data = db.fetch_one(
        """
        SELECT
            a.admin_id,
            a.user_id,
            a.nama_lengkap,

            u.username,
            u.email,
            u.is_active,
            u.created_at,
            u.last_login_at

        FROM admin a

        JOIN users u
            ON u.user_id = a.user_id

        WHERE a.user_id = %s
        """,
        (user_id,),
    )

    # Kalau admin belum mempunyai baris profil,
    # tetap tampilkan data dari users.
    if data is None:
        data = db.fetch_one(
            """
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.is_active,
                u.created_at,
                u.last_login_at
            FROM users u
            JOIN roles r
                ON r.role_id = u.role_id
            WHERE u.user_id = %s
              AND r.nama_role = 'admin'
            """,
            (user_id,),
        )

    if data is None:
        raise ValidationError("Profil admin tidak ditemukan.")

    return data


# ============================================================
# PROFIL SESUAI ROLE
# ============================================================

def profil_saya():
    pengguna = _pengguna_login()

    role = pengguna.get("role")

    if role == MAHASISWA:
        return profil_mahasiswa()

    if role == DOSEN:
        return profil_dosen()

    if role == ADMIN:
        return profil_admin()

    raise AksesDitolak("Role pengguna tidak dikenal.")


# ============================================================
# GANTI PASSWORD
# ============================================================

def ganti_password(password_lama, password_baru, konfirmasi_password):
    pengguna = _cek_role(ADMIN, DOSEN)

    password_lama = cek_wajib(
        password_lama,
        "Password lama",
    )

    password_baru = cek_password(
        password_baru,
    )

    if password_baru != konfirmasi_password:
        raise ValidationError(
            "Konfirmasi password baru tidak sama."
        )

    user_id = pengguna.get("user_id")

    data = db.fetch_one(
        """
        SELECT password_hash
        FROM users
        WHERE user_id = %s
        """,
        (user_id,),
    )

    if data is None:
        raise ValidationError(
            "Akun pengguna tidak ditemukan."
        )

    password_hash_lama = data["password_hash"]

    if not password_hash_lama:
        raise ValidationError(
            "Akun ini belum memiliki password."
        )

    if not verify_password(
        password_lama,
        password_hash_lama,
    ):
        raise ValidationError(
            "Password lama salah."
        )

    password_hash_baru = hash_password(
        password_baru
    )

    db.execute(
        """
        UPDATE users
        SET password_hash = %s
        WHERE user_id = %s
        """,
        (
            password_hash_baru,
            user_id,
        ),
    )

    return True


# ============================================================
# MAHASISWA - PENGAJUAN PERUBAHAN NIM
# ============================================================

def ajukan_perubahan_nim(
    nim_baru,
    alasan,
):
    pengguna = _cek_role(MAHASISWA)

    mahasiswa_id = pengguna.get("mahasiswa_id")

    nim_baru = cek_nim(nim_baru)
    alasan = cek_teks(
        alasan,
        "Alasan",
        255,
    )

    mahasiswa = db.fetch_one(
        """
        SELECT nim
        FROM mahasiswa
        WHERE mahasiswa_id = %s
        """,
        (mahasiswa_id,),
    )

    if mahasiswa is None:
        raise ValidationError(
            "Profil mahasiswa tidak ditemukan."
        )

    nim_lama = mahasiswa["nim"]

    if nim_baru == nim_lama:
        raise ValidationError(
            "NIM baru sama dengan NIM saat ini."
        )

    # Pastikan NIM baru belum dipakai mahasiswa lain.
    if db.fetch_one(
        """
        SELECT mahasiswa_id
        FROM mahasiswa
        WHERE nim = %s
        """,
        (nim_baru,),
    ):
        raise ValidationError(
            "NIM baru sudah digunakan oleh mahasiswa lain."
        )

    # Pastikan username juga belum digunakan.
    if db.fetch_one(
        """
        SELECT user_id
        FROM users
        WHERE username = %s
        """,
        (nim_baru,),
    ):
        raise ValidationError(
            "NIM baru sudah digunakan sebagai username akun."
        )

    # Hanya boleh ada satu pengajuan yang masih menunggu.
    pengajuan_aktif = db.fetch_one(
        """
        SELECT pengajuan_id
        FROM pengajuan_perubahan_nim
        WHERE mahasiswa_id = %s
          AND status = 'Menunggu'
        """,
        (mahasiswa_id,),
    )

    if pengajuan_aktif:
        raise ValidationError(
            "Masih ada pengajuan perubahan NIM yang menunggu diproses admin."
        )

    pengajuan_id = db.execute(
        """
        INSERT INTO pengajuan_perubahan_nim (
            mahasiswa_id,
            nim_lama,
            nim_baru,
            alasan
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            mahasiswa_id,
            nim_lama,
            nim_baru,
            alasan,
        ),
    )

    return pengajuan_id


# ============================================================
# RIWAYAT PENGAJUAN MAHASISWA
# ============================================================

def riwayat_pengajuan_nim():
    pengguna = _cek_role(MAHASISWA)

    return db.fetch_all(
        """
        SELECT
            pengajuan_id,
            nim_lama,
            nim_baru,
            alasan,
            status,
            catatan_admin,
            tanggal_pengajuan,
            tanggal_diproses
        FROM pengajuan_perubahan_nim
        WHERE mahasiswa_id = %s
        ORDER BY pengajuan_id DESC
        """,
        (pengguna.get("mahasiswa_id"),),
    )


# ============================================================
# ADMIN - DAFTAR PENGAJUAN
# ============================================================

def daftar_pengajuan_nim():
    _cek_role(ADMIN)

    return db.fetch_all(
        """
        SELECT
            p.pengajuan_id,
            p.mahasiswa_id,
            p.nim_lama,
            p.nim_baru,
            p.alasan,
            p.status,
            p.catatan_admin,
            p.tanggal_pengajuan,
            p.tanggal_diproses,

            m.nama_lengkap,

            u.username AS username_mahasiswa

        FROM pengajuan_perubahan_nim p

        JOIN mahasiswa m
            ON m.mahasiswa_id = p.mahasiswa_id

        JOIN users u
            ON u.user_id = m.user_id

        ORDER BY
            CASE
                WHEN p.status = 'Menunggu' THEN 0
                ELSE 1
            END,
            p.pengajuan_id DESC
        """
    )


# ============================================================
# ADMIN - SETUJUI PENGAJUAN
# ============================================================

def setujui_pengajuan_nim(
    pengajuan_id,
    catatan_admin=None,
):
    pengguna = _cek_role(ADMIN)

    pengajuan = db.fetch_one(
        """
        SELECT
            p.pengajuan_id,
            p.mahasiswa_id,
            p.nim_lama,
            p.nim_baru,
            p.status,

            m.user_id

        FROM pengajuan_perubahan_nim p

        JOIN mahasiswa m
            ON m.mahasiswa_id = p.mahasiswa_id

        WHERE p.pengajuan_id = %s
        """,
        (pengajuan_id,),
    )

    if pengajuan is None:
        raise ValidationError(
            "Pengajuan tidak ditemukan."
        )

    if pengajuan["status"] != "Menunggu":
        raise ValidationError(
            "Pengajuan ini sudah diproses."
        )

    nim_baru = pengajuan["nim_baru"]

    # Cek ulang karena kondisi database bisa berubah
    # setelah mahasiswa mengirim pengajuan.
    mahasiswa_lain = db.fetch_one(
        """
        SELECT mahasiswa_id
        FROM mahasiswa
        WHERE nim = %s
          AND mahasiswa_id <> %s
        """,
        (
            nim_baru,
            pengajuan["mahasiswa_id"],
        ),
    )

    if mahasiswa_lain:
        raise ValidationError(
            "NIM baru sudah digunakan mahasiswa lain."
        )

    user_lain = db.fetch_one(
        """
        SELECT user_id
        FROM users
        WHERE username = %s
          AND user_id <> %s
        """,
        (
            nim_baru,
            pengajuan["user_id"],
        ),
    )

    if user_lain:
        raise ValidationError(
            "NIM baru sudah digunakan sebagai username akun lain."
        )

    catatan_admin = (
        None
        if catatan_admin is None
        else str(catatan_admin).strip() or None
    )

    with db.db_cursor(commit=True) as cur:

        # Update username akun mahasiswa.
        cur.execute(
            """
            UPDATE users
            SET username = %s
            WHERE user_id = %s
            """,
            (
                nim_baru,
                pengajuan["user_id"],
            ),
        )

        # Update NIM profil mahasiswa.
        cur.execute(
            """
            UPDATE mahasiswa
            SET nim = %s
            WHERE mahasiswa_id = %s
            """,
            (
                nim_baru,
                pengajuan["mahasiswa_id"],
            ),
        )

        # Tandai pengajuan sudah disetujui.
        cur.execute(
            """
            UPDATE pengajuan_perubahan_nim
            SET
                status = 'Disetujui',
                diproses_oleh = %s,
                catatan_admin = %s,
                tanggal_diproses = %s
            WHERE pengajuan_id = %s
            """,
            (
                pengguna.get("user_id"),
                catatan_admin,
                datetime.now(),
                pengajuan_id,
            ),
        )

    return True


# ============================================================
# ADMIN - TOLAK PENGAJUAN
# ============================================================

def tolak_pengajuan_nim(
    pengajuan_id,
    catatan_admin,
):
    pengguna = _cek_role(ADMIN)

    catatan_admin = cek_teks(
        catatan_admin,
        "Catatan admin",
        255,
    )

    pengajuan = db.fetch_one(
        """
        SELECT status
        FROM pengajuan_perubahan_nim
        WHERE pengajuan_id = %s
        """,
        (pengajuan_id,),
    )

    if pengajuan is None:
        raise ValidationError(
            "Pengajuan tidak ditemukan."
        )

    if pengajuan["status"] != "Menunggu":
        raise ValidationError(
            "Pengajuan ini sudah diproses."
        )

    db.execute(
        """
        UPDATE pengajuan_perubahan_nim
        SET
            status = 'Ditolak',
            diproses_oleh = %s,
            catatan_admin = %s,
            tanggal_diproses = %s
        WHERE pengajuan_id = %s
        """,
        (
            pengguna.get("user_id"),
            catatan_admin,
            datetime.now(),
            pengajuan_id,
        ),
    )

    return True