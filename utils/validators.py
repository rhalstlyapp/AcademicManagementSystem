<<<<<<< HEAD
"""Validasi input dan kelas error aplikasi.

Semua error yang pesannya aman ditampilkan ke pengguna mewarisi AppError,
sehingga GUI cukup menangkap AppError:

    try:
        mahasiswa.tambah(...)
    except AppError as err:
        tampilkan_pesan(str(err))
"""
import re
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


class AppError(Exception):
    """Error yang pesannya aman ditampilkan ke pengguna."""


class ValidationError(AppError):
    """Input tidak valid atau melanggar aturan data."""


class AuthError(AppError):
    """Login gagal."""


class AksesDitolak(AppError):
    """Pengguna tidak berhak melakukan tindakan ini."""


def cek_wajib(nilai, label):
    teks = ("" if nilai is None else str(nilai)).strip()
    if not teks:
        raise ValidationError(f"{label} wajib diisi.")
    return teks


def cek_teks(nilai, label, maks):
    teks = cek_wajib(nilai, label)
    if len(teks) > maks:
        raise ValidationError(f"{label} maksimal {maks} karakter.")
    return teks


def cek_id(nilai, label):
    try:
        angka = int(nilai)
    except (TypeError, ValueError):
        raise ValidationError(f"{label} tidak valid.") from None
    if angka <= 0:
        raise ValidationError(f"{label} tidak valid.")
    return angka


def nim_input_diizinkan(nilai):
    """Izinkan input NIM kosong/sebagian saat mengetik, hanya angka maksimal 9 digit."""
    teks = str(nilai)
    return len(teks) <= 9 and (teks == "" or (teks.isascii() and teks.isdigit()))


def cek_nim(nim):
    nim = cek_wajib(nim, "NIM")
    if not re.fullmatch(r"[0-9]{9}", nim):
        raise ValidationError("NIM harus tepat 9 digit angka.")
    return nim


def cek_nilai(nilai, label):
    """Nilai 0-100 dengan 2 desimal. Menerima koma sebagai pemisah desimal."""
    teks = cek_wajib(nilai, label).replace(",", ".")
    try:
        angka = Decimal(teks)
    except InvalidOperation:
        raise ValidationError(f"{label} harus berupa angka.") from None
    if not angka.is_finite() or angka < 0 or angka > 100:
        raise ValidationError(f"{label} harus antara 0 dan 100.")
    return angka.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cek_sks(sks):
    try:
        angka = int(str(sks).strip())
    except (TypeError, ValueError):
        raise ValidationError("SKS harus berupa angka bulat.") from None
    if not 1 <= angka <= 6:
        raise ValidationError("SKS harus antara 1 dan 6.")
    return angka


def cek_angkatan(angkatan):
    try:
        angka = int(str(angkatan).strip())
    except (TypeError, ValueError):
        raise ValidationError("Angkatan harus berupa angka (contoh 2025).") from None
    if not 1990 <= angka <= 2100:
        raise ValidationError("Angkatan harus antara 1990 dan 2100.")
    return angka


def cek_kode_semester(kode):
    kode = cek_wajib(kode, "Kode semester")
    if not re.fullmatch(r"\d{4}[123]", kode):
        raise ValidationError(
            "Kode semester harus 5 digit: tahun + 1 (Ganjil), 2 (Genap), atau 3 (Pendek). Contoh: 20251."
        )
    return kode


def cek_username(username):
    username = cek_wajib(username, "Username")
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,50}", username):
        raise ValidationError("Username 3-50 karakter: huruf, angka, titik, garis bawah, atau strip.")
    return username


def cek_password(password):
    if password is None or len(password) < 8:
        raise ValidationError("Password minimal 8 karakter.")
    if len(password.encode("utf-8")) > 72:
        raise ValidationError("Password terlalu panjang (maksimal 72 byte).")
    return password


def cek_tanggal(nilai, label="Tanggal"):
    """Menerima date atau teks YYYY-MM-DD. Mengembalikan objek date."""
    if isinstance(nilai, datetime):
        hasil = nilai.date()
    elif isinstance(nilai, date):
        hasil = nilai
    else:
        teks = cek_wajib(nilai, label)
        try:
            hasil = datetime.strptime(teks, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(f"{label} harus berformat TTTT-BB-HH (contoh 2006-03-14).") from None
    if hasil.year < 1900 or hasil > date.today():
        raise ValidationError(f"{label} tidak masuk akal.")
    return hasil


def cek_pilihan(nilai, pilihan, label):
    if nilai not in pilihan:
        raise ValidationError(f"{label} harus salah satu dari: {', '.join(pilihan)}.")
    return nilai


def pola_cari(keyword):
    """Mengubah kata kunci menjadi pola LIKE, atau None bila kosong."""
    teks = ("" if keyword is None else str(keyword)).strip()
    return f"%{teks}%" if teks else None


def rapikan_spasi(teks):
    """Menghapus spasi berlebih: '  Budi   Santoso ' menjadi 'Budi Santoso'."""
    return " ".join(("" if teks is None else str(teks)).split())


def normal_nama(teks):
    """Bentuk pembanding nama: tanpa spasi berlebih dan tidak peka huruf besar/kecil."""
    return rapikan_spasi(teks).casefold()


def cek_nama_orang(nama, label="Nama"):
    nama = rapikan_spasi(cek_wajib(nama, label))
    if len(nama) < 2:
        raise ValidationError(f"{label} terlalu pendek.")
    if len(nama) > 100:
        raise ValidationError(f"{label} maksimal 100 karakter.")
    if re.search(r"\d", nama):
        raise ValidationError(f"{label} tidak boleh mengandung angka.")
    return nama


def opsional(nilai, fungsi, *args):
    """Menjalankan validasi hanya bila nilai terisi; kosong menjadi None."""
    if nilai is None or str(nilai).strip() == "":
        return None
    return fungsi(nilai, *args)
=======
"""Validasi input dan kelas error aplikasi.

Semua error yang pesannya aman ditampilkan ke pengguna mewarisi AppError,
sehingga GUI cukup menangkap AppError:

    try:
        mahasiswa.tambah(...)
    except AppError as err:
        tampilkan_pesan(str(err))
"""
import re
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


class AppError(Exception):
    """Error yang pesannya aman ditampilkan ke pengguna."""


class ValidationError(AppError):
    """Input tidak valid atau melanggar aturan data."""


class AuthError(AppError):
    """Login gagal."""


class AksesDitolak(AppError):
    """Pengguna tidak berhak melakukan tindakan ini."""


def cek_wajib(nilai, label):
    teks = ("" if nilai is None else str(nilai)).strip()
    if not teks:
        raise ValidationError(f"{label} wajib diisi.")
    return teks


def cek_teks(nilai, label, maks):
    teks = cek_wajib(nilai, label)
    if len(teks) > maks:
        raise ValidationError(f"{label} maksimal {maks} karakter.")
    return teks


def cek_id(nilai, label):
    try:
        angka = int(nilai)
    except (TypeError, ValueError):
        raise ValidationError(f"{label} tidak valid.") from None
    if angka <= 0:
        raise ValidationError(f"{label} tidak valid.")
    return angka


def cek_nim(nim):
    nim = cek_wajib(nim, "NIM")
    if not re.fullmatch(r"[0-9A-Za-z]{5,15}", nim):
        raise ValidationError("NIM harus 5-15 karakter berupa huruf atau angka.")
    return nim


def cek_nilai(nilai, label):
    """Nilai 0-100 dengan 2 desimal. Menerima koma sebagai pemisah desimal."""
    teks = cek_wajib(nilai, label).replace(",", ".")
    try:
        angka = Decimal(teks)
    except InvalidOperation:
        raise ValidationError(f"{label} harus berupa angka.") from None
    if not angka.is_finite() or angka < 0 or angka > 100:
        raise ValidationError(f"{label} harus antara 0 dan 100.")
    return angka.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cek_sks(sks):
    try:
        angka = int(str(sks).strip())
    except (TypeError, ValueError):
        raise ValidationError("SKS harus berupa angka bulat.") from None
    if not 1 <= angka <= 6:
        raise ValidationError("SKS harus antara 1 dan 6.")
    return angka


def cek_angkatan(angkatan):
    try:
        angka = int(str(angkatan).strip())
    except (TypeError, ValueError):
        raise ValidationError("Angkatan harus berupa angka (contoh 2025).") from None
    if not 1990 <= angka <= 2100:
        raise ValidationError("Angkatan harus antara 1990 dan 2100.")
    return angka


def cek_kode_semester(kode):
    kode = cek_wajib(kode, "Kode semester")
    if not re.fullmatch(r"\d{4}[123]", kode):
        raise ValidationError(
            "Kode semester harus 5 digit: tahun + 1 (Ganjil), 2 (Genap), atau 3 (Pendek). Contoh: 20251."
        )
    return kode


def cek_username(username):
    username = cek_wajib(username, "Username")
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,50}", username):
        raise ValidationError("Username 3-50 karakter: huruf, angka, titik, garis bawah, atau strip.")
    return username


def cek_password(password):
    if password is None or len(password) < 8:
        raise ValidationError("Password minimal 8 karakter.")
    if len(password.encode("utf-8")) > 72:
        raise ValidationError("Password terlalu panjang (maksimal 72 byte).")
    return password


def cek_tanggal(nilai, label="Tanggal"):
    """Menerima date atau teks YYYY-MM-DD. Mengembalikan objek date."""
    if isinstance(nilai, datetime):
        hasil = nilai.date()
    elif isinstance(nilai, date):
        hasil = nilai
    else:
        teks = cek_wajib(nilai, label)
        try:
            hasil = datetime.strptime(teks, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(f"{label} harus berformat TTTT-BB-HH (contoh 2006-03-14).") from None
    if hasil.year < 1900 or hasil > date.today():
        raise ValidationError(f"{label} tidak masuk akal.")
    return hasil


def cek_pilihan(nilai, pilihan, label):
    if nilai not in pilihan:
        raise ValidationError(f"{label} harus salah satu dari: {', '.join(pilihan)}.")
    return nilai


def pola_cari(keyword):
    """Mengubah kata kunci menjadi pola LIKE, atau None bila kosong."""
    teks = ("" if keyword is None else str(keyword)).strip()
    return f"%{teks}%" if teks else None


def rapikan_spasi(teks):
    """Menghapus spasi berlebih: '  Budi   Santoso ' menjadi 'Budi Santoso'."""
    return " ".join(("" if teks is None else str(teks)).split())


def normal_nama(teks):
    """Bentuk pembanding nama: tanpa spasi berlebih dan tidak peka huruf besar/kecil."""
    return rapikan_spasi(teks).casefold()


def cek_nama_orang(nama, label="Nama"):
    nama = rapikan_spasi(cek_wajib(nama, label))
    if len(nama) < 2:
        raise ValidationError(f"{label} terlalu pendek.")
    if len(nama) > 100:
        raise ValidationError(f"{label} maksimal 100 karakter.")
    if re.search(r"\d", nama):
        raise ValidationError(f"{label} tidak boleh mengandung angka.")
    return nama


def opsional(nilai, fungsi, *args):
    """Menjalankan validasi hanya bila nilai terisi; kosong menjadi None."""
    if nilai is None or str(nilai).strip() == "":
        return None
    return fungsi(nilai, *args)
>>>>>>> 4cca13e (feat: NIM as primary key, Nama+NIM login, registration, jurusan)
