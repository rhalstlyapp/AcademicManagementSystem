"""Pencarian dan pengelolaan profil mahasiswa sesuai database/schema.sql."""
from database import connection as db
from utils.permissions import ADMIN, DOSEN, require_role
from utils.validators import (
    ValidationError,
    cek_angkatan,
    cek_id,
    cek_nama_orang,
    cek_nim,
    cek_pilihan,
    cek_tanggal,
    pola_cari,
)

STATUS = ("Aktif", "Cuti", "Lulus", "DO", "Keluar")

_SELECT = (
    "SELECT m.mahasiswa_id, m.user_id, m.nim, m.nama_lengkap, m.jenis_kelamin, "
    "m.tempat_lahir, m.tanggal_lahir, m.agama, m.nik, m.alamat, m.no_hp, "
    "m.nama_ayah, m.nama_ibu, m.angkatan, m.status_mahasiswa, m.prodi_id, "
    "p.kode_prodi, p.nama_prodi, p.jenjang, j.jurusan_id, j.kode_jurusan, "
    "j.nama_jurusan, m.dosen_pa_id, d.nama_lengkap AS nama_dosen_pa "
    "FROM mahasiswa m JOIN program_studi p ON p.prodi_id = m.prodi_id "
    "JOIN jurusan j ON j.jurusan_id = p.jurusan_id "
    "LEFT JOIN dosen d ON d.dosen_id = m.dosen_pa_id "
)


@require_role(ADMIN, DOSEN)
def daftar(keyword=None, jurusan_id=None, prodi_id=None, angkatan=None, status=None):
    """Daftar mahasiswa, bisa dicari dan difilter berdasarkan relasi akademik."""
    sql = _SELECT + " WHERE 1 = 1"
    params = []
    pola = pola_cari(keyword)
    if pola:
        sql += " AND (m.nim LIKE %s OR m.nama_lengkap LIKE %s)"
        params.extend((pola, pola))
    if jurusan_id is not None:
        sql += " AND j.jurusan_id = %s"
        params.append(cek_id(jurusan_id, "Jurusan"))
    if prodi_id is not None:
        sql += " AND m.prodi_id = %s"
        params.append(cek_id(prodi_id, "Program studi"))
    if angkatan is not None:
        sql += " AND m.angkatan = %s"
        params.append(cek_angkatan(angkatan))
    if status:
        sql += " AND m.status_mahasiswa = %s"
        params.append(cek_pilihan(status, STATUS, "Status"))
    return db.fetch_all(sql + " ORDER BY m.nama_lengkap, m.nim", tuple(params))


@require_role(ADMIN, DOSEN)
def detail(mahasiswa_id):
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    row = db.fetch_one(_SELECT + " WHERE m.mahasiswa_id = %s", (mahasiswa_id,))
    if row is None:
        raise ValidationError("Mahasiswa tidak ditemukan.")
    return row


@require_role(ADMIN, DOSEN)
def get(nim):
    nim = cek_nim(nim)
    row = db.fetch_one(_SELECT + " WHERE m.nim = %s", (nim,))
    if row is None:
        raise ValidationError("Mahasiswa tidak ditemukan.")
    return row


@require_role(ADMIN)
def tambah(
    username, email, password, nim, nama, prodi_id, dosen_pa_id,
    jenis_kelamin, tanggal_lahir, angkatan, **biodata,
):
    """Alias service untuk registrasi yang membuat akun dan profil sekaligus."""
    from backend.auth import registrasi

    return registrasi(
        username, email, password, nim, nama, prodi_id, dosen_pa_id,
        jenis_kelamin, tanggal_lahir, angkatan, **biodata,
    )


@require_role(ADMIN)
def ubah_profil(
    mahasiswa_id, nama, prodi_id, dosen_pa_id, jenis_kelamin, tanggal_lahir,
    angkatan, status, tempat_lahir=None, agama=None, nik=None, alamat=None,
    no_hp=None, nama_ayah=None, nama_ibu=None,
):
    """Ubah profil mahasiswa tanpa mengganti akun login atau NIM."""
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    nama = cek_nama_orang(nama, "Nama")
    prodi_id = cek_id(prodi_id, "Program studi")
    dosen_pa_id = cek_id(dosen_pa_id, "Dosen PA")
    jenis_kelamin = (jenis_kelamin or "").strip().upper()
    if jenis_kelamin not in ("L", "P"):
        raise ValidationError("Jenis kelamin harus L atau P.")
    tanggal_lahir = cek_tanggal(tanggal_lahir, "Tanggal lahir")
    angkatan = cek_angkatan(angkatan)
    status = cek_pilihan(status, STATUS, "Status")
    if db.fetch_one("SELECT prodi_id FROM program_studi WHERE prodi_id = %s", (prodi_id,)) is None:
        raise ValidationError("Program studi tidak ditemukan.")
    if db.fetch_one(
        "SELECT dosen_id FROM dosen WHERE dosen_id = %s AND prodi_id = %s AND status = 'Aktif'",
        (dosen_pa_id, prodi_id),
    ) is None:
        raise ValidationError("Dosen PA harus dosen aktif dari program studi yang dipilih.")
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

    db.execute(
        "UPDATE mahasiswa SET nama_lengkap = %s, prodi_id = %s, dosen_pa_id = %s, "
        "jenis_kelamin = %s, tanggal_lahir = %s, angkatan = %s, status_mahasiswa = %s, "
        "tempat_lahir = %s, agama = %s, nik = %s, alamat = %s, no_hp = %s, "
        "nama_ayah = %s, nama_ibu = %s WHERE mahasiswa_id = %s",
        (nama, prodi_id, dosen_pa_id, jenis_kelamin, tanggal_lahir, angkatan, status,
         tempat_lahir, agama, nik, alamat, no_hp, nama_ayah, nama_ibu, mahasiswa_id),
    )
    return detail(mahasiswa_id)


@require_role(ADMIN)
def ubah_status(mahasiswa_id, status):
    mahasiswa_id = cek_id(mahasiswa_id, "Mahasiswa")
    status = cek_pilihan(status, STATUS, "Status")
    if db.fetch_one("SELECT mahasiswa_id FROM mahasiswa WHERE mahasiswa_id = %s", (mahasiswa_id,)) is None:
        raise ValidationError("Mahasiswa tidak ditemukan.")
    db.execute(
        "UPDATE mahasiswa SET status_mahasiswa = %s WHERE mahasiswa_id = %s",
        (status, mahasiswa_id),
    )
    return detail(mahasiswa_id)
