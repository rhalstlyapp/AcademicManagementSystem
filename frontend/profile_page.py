"""Halaman profil pengguna SIAKAD."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from assets import colors as c
from backend import profile
from utils import session
from utils.validators import AppError


# ============================================================
# KONFIGURASI
# ============================================================

FONT_JUDUL = c.FONT_TITLE
FONT_SUBJUDUL = c.FONT_HEADING
FONT_NORMAL = c.FONT_BODY
FONT_KETERANGAN = c.FONT_SMALL

WARNA_KARTU = c.CARD_BG
WARNA_BORDER = c.BORDER_COLOR
WARNA_TEKS = c.TEXT_DARK
WARNA_SEKUNDER = c.TEXT_MUTED
WARNA_UTAMA = c.PRIMARY_COLOR

# ============================================================
# BANTUAN TAMPILAN
# ============================================================

def _bersihkan(parent):
    """Menghapus seluruh widget dari halaman."""
    for widget in parent.winfo_children():
        widget.destroy()


def _buat_kartu(parent):
    """Membuat frame kartu putih."""
    return tk.Frame(
        parent,
        bg=WARNA_KARTU,
        highlightbackground=WARNA_BORDER,
        highlightthickness=1,
        bd=0,
    )


def _buat_label_info(parent, judul, nilai, baris):
    """Membuat satu baris informasi profil."""

    tk.Label(
        parent,
        text=judul,
        font=FONT_KETERANGAN,
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
        anchor="w",
    ).grid(
        row=baris,
        column=0,
        sticky="w",
        padx=(20, 30),
        pady=(10, 2),
    )

    tk.Label(
        parent,
        text=nilai or "-",
        font=FONT_NORMAL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
        anchor="w",
    ).grid(
        row=baris,
        column=1,
        sticky="w",
        padx=(0, 20),
        pady=(10, 2),
    )


def _nilai(data, key):
    """Mengambil nilai dictionary dengan aman."""
    value = data.get(key)
    return "-" if value in (None, "") else str(value)


# ============================================================
# FOTO PROFIL
# ============================================================

def _tampilkan_foto(parent, data):
    """Menampilkan foto profil atau avatar default."""

    foto_path = data.get("foto_profil")

    area = tk.Frame(
        parent,
        bg=WARNA_KARTU,
        width=180,
        height=180,
    )
    area.grid_propagate(False)

    if foto_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path_foto = os.path.join(base_dir, foto_path)

        if os.path.exists(path_foto):
            try:
                gambar = Image.open(path_foto)
                gambar.thumbnail((150, 150))

                foto = ImageTk.PhotoImage(gambar)

                label = tk.Label(
                    area,
                    image=foto,
                    bg=WARNA_KARTU,
                )
                label.image = foto
                label.pack(expand=True)

                return area

            except Exception:
                pass

    tk.Label(
        area,
        text="👤",
        font=("Segoe UI Emoji", 55),
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
    ).pack(expand=True)

    return area


def _pilih_foto(parent, refresh):
    """Memilih dan menyimpan foto profil."""

    path_file = filedialog.askopenfilename(
        parent=parent,
        title="Pilih Foto Profil",
        filetypes=[
            (
                "File gambar",
                "*.jpg *.jpeg *.png *.webp",
            ),
            ("Semua file", "*.*"),
        ],
    )

    if not path_file:
        return

    try:
        profile.simpan_foto_profil(path_file)

        messagebox.showinfo(
            "Foto Profil",
            "Foto profil berhasil diperbarui.",
            parent=parent,
        )

        refresh()

    except AppError as exc:
        messagebox.showerror(
            "Gagal",
            str(exc),
            parent=parent,
        )

    except Exception as exc:
        messagebox.showerror(
            "Gagal",
            f"Foto gagal disimpan.\n\n{exc}",
            parent=parent,
        )


def _hapus_foto(parent, refresh):
    """Menghapus foto profil."""

    if not messagebox.askyesno(
        "Hapus Foto",
        "Yakin ingin menghapus foto profil?",
        parent=parent,
    ):
        return

    try:
        profile.hapus_foto_profil()

        messagebox.showinfo(
            "Foto Profil",
            "Foto profil berhasil dihapus.",
            parent=parent,
        )

        refresh()

    except AppError as exc:
        messagebox.showerror(
            "Gagal",
            str(exc),
            parent=parent,
        )

    except Exception as exc:
        messagebox.showerror(
            "Gagal",
            f"Foto gagal dihapus.\n\n{exc}",
            parent=parent,
        )


# ============================================================
# GANTI PASSWORD
# ============================================================

def _dialog_ganti_password(parent):
    """Dialog untuk mengganti password."""

    dialog = tk.Toplevel(parent)
    dialog.title("Ganti Password")
    dialog.configure(bg=c.BG_COLOR)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    frame = tk.Frame(
        dialog,
        bg=WARNA_KARTU,
        padx=25,
        pady=25,
    )
    frame.pack(padx=20, pady=20)

    tk.Label(
        frame,
        text="Ganti Password",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(0, 20),
    )

    fields = [
        ("Password lama", False),
        ("Password baru", False),
        ("Konfirmasi password baru", False),
    ]

    entries = []

    for index, (label, _) in enumerate(fields, start=1):
        tk.Label(
            frame,
            text=label,
            font=FONT_NORMAL,
            fg=WARNA_TEKS,
            bg=WARNA_KARTU,
        ).grid(
            row=index,
            column=0,
            sticky="w",
            pady=8,
        )

        entry = tk.Entry(
            frame,
            width=30,
            font=FONT_NORMAL,
            show="•",
        )
        entry.grid(
            row=index,
            column=1,
            padx=(15, 0),
            pady=8,
        )

        entries.append(entry)

    def simpan():
        try:
            profile.ganti_password(
                entries[0].get(),
                entries[1].get(),
                entries[2].get(),
            )

            messagebox.showinfo(
                "Berhasil",
                "Password berhasil diubah.",
                parent=dialog,
            )

            dialog.destroy()

        except AppError as exc:
            messagebox.showerror(
                "Gagal",
                str(exc),
                parent=dialog,
            )

        except Exception as exc:
            messagebox.showerror(
                "Gagal",
                f"Password gagal diubah.\n\n{exc}",
                parent=dialog,
            )

tk.Button(
    frame,
    text="Simpan Password",
    command=simpan,
    bg=WARNA_UTAMA,
    fg="white",
    activebackground=c.PRIMARY_HOVER,
    activeforeground="white",
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2",
).grid(
    row=4,
    column=0,
    columnspan=2,
    sticky="e",
    pady=(18, 0),
)


# ============================================================
# MAHASISWA - PENGAJUAN NIM
# ============================================================

def _dialog_pengajuan_nim(parent, refresh):
    """Dialog pengajuan perubahan NIM."""

    dialog = tk.Toplevel(parent)
    dialog.title("Pengajuan Perubahan NIM")
    dialog.configure(bg=c.BG_COLOR)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    frame = tk.Frame(
        dialog,
        bg=WARNA_KARTU,
        padx=25,
        pady=25,
    )
    frame.pack(padx=20, pady=20)

    tk.Label(
        frame,
        text="Pengajuan Perubahan NIM",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="w",
        pady=(0, 20),
    )

    tk.Label(
        frame,
        text="NIM baru",
        font=FONT_NORMAL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).grid(
        row=1,
        column=0,
        sticky="w",
        pady=8,
    )

    in_nim = tk.Entry(
        frame,
        width=30,
        font=FONT_NORMAL,
    )
    in_nim.grid(
        row=1,
        column=1,
        padx=(15, 0),
        pady=8,
    )

    tk.Label(
        frame,
        text="Alasan",
        font=FONT_NORMAL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).grid(
        row=2,
        column=0,
        sticky="nw",
        pady=8,
    )

    in_alasan = tk.Text(
        frame,
        width=30,
        height=5,
        font=FONT_NORMAL,
    )
    in_alasan.grid(
        row=2,
        column=1,
        padx=(15, 0),
        pady=8,
    )

    def kirim():
        try:
            profile.ajukan_perubahan_nim(
                in_nim.get(),
                in_alasan.get("1.0", "end"),
            )

            messagebox.showinfo(
                "Berhasil",
                "Pengajuan perubahan NIM berhasil dikirim.",
                parent=dialog,
            )

            dialog.destroy()
            refresh()

        except AppError as exc:
            messagebox.showerror(
                "Gagal",
                str(exc),
                parent=dialog,
            )

        except Exception as exc:
            messagebox.showerror(
                "Gagal",
                f"Pengajuan gagal dikirim.\n\n{exc}",
                parent=dialog,
            )

    tk.Button(
        frame,
        text="Kirim Pengajuan",
        command=kirim,
        bg=WARNA_UTAMA,
        fg="white",
        activebackground=WARNA_UTAMA,
        activeforeground="white",
        relief="flat",
        padx=15,
        pady=8,
        cursor="hand2",
    ).grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="e",
        pady=(15, 0),
    )


# ============================================================
# MAHASISWA
# ============================================================

def _tampilkan_mahasiswa(parent, data, refresh):
    """Tampilan profil mahasiswa."""

    kartu = _buat_kartu(parent)
    kartu.pack(fill="x", padx=20, pady=(0, 15))

    kiri = tk.Frame(kartu, bg=WARNA_KARTU)
    kiri.pack(side="left", padx=20, pady=20)

    _tampilkan_foto(kiri, data).pack()

    tk.Button(
        kiri,
        text="Ganti Foto",
        command=lambda: _pilih_foto(parent, refresh),
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
    ).pack(fill="x", pady=(10, 5))

    if data.get("foto_profil"):
        tk.Button(
            kiri,
            text="Hapus Foto",
            command=lambda: _hapus_foto(parent, refresh),
            bg=WARNA_KARTU,
            fg=WARNA_TEKS,
            relief="flat",
            cursor="hand2",
        ).pack(fill="x")

    kanan = tk.Frame(kartu, bg=WARNA_KARTU)
    kanan.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 20),
        pady=20,
    )

    tk.Label(
        kanan,
        text=_nilai(data, "nama_lengkap"),
        font=("Segoe UI", 17, "bold"),
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w")

    tk.Label(
        kanan,
        text=f"NIM {_nilai(data, 'nim')}",
        font=FONT_NORMAL,
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
    ).pack(anchor="w", pady=(3, 15))

    info = tk.Frame(kanan, bg=WARNA_KARTU)
    info.pack(fill="x")

    _buat_label_info(
        info,
        "Program Studi",
        f"{_nilai(data, 'kode_prodi')} - {_nilai(data, 'nama_prodi')}",
        0,
    )
    _buat_label_info(
        info,
        "Jenjang",
        _nilai(data, "jenjang"),
        1,
    )
    _buat_label_info(
        info,
        "Dosen PA",
        _nilai(data, "nama_dosen_pa"),
        2,
    )
    _buat_label_info(
        info,
        "Angkatan",
        _nilai(data, "angkatan"),
        3,
    )
    _buat_label_info(
        info,
        "Status",
        _nilai(data, "status_mahasiswa"),
        4,
    )

    kartu_detail = _buat_kartu(parent)
    kartu_detail.pack(fill="x", padx=20, pady=(0, 15))

    tk.Label(
        kartu_detail,
        text="Informasi Pribadi",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w", padx=20, pady=(20, 10))

    detail = tk.Frame(kartu_detail, bg=WARNA_KARTU)
    detail.pack(fill="x", padx=20, pady=(0, 20))

    _buat_label_info(
        detail,
        "Jenis Kelamin",
        _nilai(data, "jenis_kelamin"),
        0,
    )
    _buat_label_info(
        detail,
        "Tempat Lahir",
        _nilai(data, "tempat_lahir"),
        1,
    )
    _buat_label_info(
        detail,
        "Tanggal Lahir",
        _nilai(data, "tanggal_lahir"),
        2,
    )
    _buat_label_info(
        detail,
        "Agama",
        _nilai(data, "agama"),
        3,
    )
    _buat_label_info(
        detail,
        "NIK",
        _nilai(data, "nik"),
        4,
    )
    _buat_label_info(
        detail,
        "Alamat",
        _nilai(data, "alamat"),
        5,
    )
    _buat_label_info(
        detail,
        "No. HP",
        _nilai(data, "no_hp"),
        6,
    )
    _buat_label_info(
        detail,
        "Nama Ayah",
        _nilai(data, "nama_ayah"),
        7,
    )
    _buat_label_info(
        detail,
        "Nama Ibu",
        _nilai(data, "nama_ibu"),
        8,
    )

    kartu_nim = _buat_kartu(parent)
    kartu_nim.pack(fill="x", padx=20, pady=(0, 20))

    tk.Label(
        kartu_nim,
        text="Perubahan NIM",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(
        kartu_nim,
        text=(
            "Jika terdapat kesalahan pada NIM, mahasiswa dapat "
            "mengajukan perubahan kepada admin."
        ),
        font=FONT_KETERANGAN,
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
        wraplength=650,
        justify="left",
    ).pack(anchor="w", padx=20, pady=(0, 12))

    tk.Button(
        kartu_nim,
        text="Ajukan Perubahan NIM",
        command=lambda: _dialog_pengajuan_nim(parent, refresh),
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
    ).pack(anchor="w", padx=20, pady=(0, 15))

    riwayat = profile.riwayat_pengajuan_nim()

    if riwayat:
        tk.Label(
            kartu_nim,
            text="Riwayat Pengajuan",
            font=("Segoe UI", 10, "bold"),
            fg=WARNA_TEKS,
            bg=WARNA_KARTU,
        ).pack(anchor="w", padx=20, pady=(0, 8))

        for item in riwayat:
            status = item["status"]

            teks = (
                f"{item['nim_lama']} → {item['nim_baru']}    "
                f"Status: {status}\n"
                f"Alasan: {item['alasan']}"
            )

            if item.get("catatan_admin"):
                teks += f"\nCatatan admin: {item['catatan_admin']}"

            tk.Label(
                kartu_nim,
                text=teks,
                font=FONT_KETERANGAN,
                fg=WARNA_TEKS,
                bg=WARNA_KARTU,
                justify="left",
                anchor="w",
            ).pack(
                fill="x",
                padx=20,
                pady=(0, 12),
            )


# ============================================================
# DOSEN
# ============================================================

def _tampilkan_dosen(parent, data, refresh):
    """Tampilan profil dosen."""

    kartu = _buat_kartu(parent)
    kartu.pack(fill="x", padx=20, pady=(0, 15))

    kiri = tk.Frame(kartu, bg=WARNA_KARTU)
    kiri.pack(side="left", padx=20, pady=20)

    _tampilkan_foto(kiri, data).pack()

    tk.Button(
        kiri,
        text="Ganti Foto",
        command=lambda: _pilih_foto(parent, refresh),
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
    ).pack(fill="x", pady=(10, 5))

    if data.get("foto_profil"):
        tk.Button(
            kiri,
            text="Hapus Foto",
            command=lambda: _hapus_foto(parent, refresh),
            bg=WARNA_KARTU,
            fg=WARNA_TEKS,
            relief="flat",
            cursor="hand2",
        ).pack(fill="x")

    kanan = tk.Frame(kartu, bg=WARNA_KARTU)
    kanan.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 20),
        pady=20,
    )

    tk.Label(
        kanan,
        text=_nilai(data, "nama_lengkap"),
        font=("Segoe UI", 17, "bold"),
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w")

    tk.Label(
        kanan,
        text="Dosen",
        font=FONT_NORMAL,
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
    ).pack(anchor="w", pady=(3, 15))

    info = tk.Frame(kanan, bg=WARNA_KARTU)
    info.pack(fill="x")

    _buat_label_info(info, "NIDN", _nilai(data, "nidn"), 0)
    _buat_label_info(info, "NIP", _nilai(data, "nip"), 1)
    _buat_label_info(info, "Program Studi", f"{_nilai(data, 'kode_prodi')} - {_nilai(data, 'nama_prodi')}", 2)
    _buat_label_info(info, "Jenjang", _nilai(data, "jenjang"), 3)
    _buat_label_info(info, "Username", _nilai(data, "username"), 4)
    _buat_label_info(info, "Email", _nilai(data, "email"), 5)
    _buat_label_info(info, "Status", _nilai(data, "status"), 6)

    kartu_password = _buat_kartu(parent)
    kartu_password.pack(fill="x", padx=20, pady=(0, 20))

    tk.Label(
        kartu_password,
        text="Keamanan Akun",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Label(
        kartu_password,
        text="Ubah password akun secara berkala untuk menjaga keamanan.",
        font=FONT_KETERANGAN,
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
    ).pack(anchor="w", padx=20)

    tk.Button(
        kartu_password,
        text="Ganti Password",
        command=lambda: _dialog_ganti_password(parent),
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
    ).pack(anchor="w", padx=20, pady=15)


# ============================================================
# ADMIN
# ============================================================

def _tampilkan_admin(parent, data, refresh):
    """Tampilan profil admin."""

    kartu = _buat_kartu(parent)
    kartu.pack(fill="x", padx=20, pady=(0, 15))

    kiri = tk.Frame(kartu, bg=WARNA_KARTU)
    kiri.pack(side="left", padx=20, pady=20)

    _tampilkan_foto(kiri, data).pack()

    tk.Button(
        kiri,
        text="Ganti Foto",
        command=lambda: _pilih_foto(parent, refresh),
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
    ).pack(fill="x", pady=(10, 5))

    if data.get("foto_profil"):
        tk.Button(
            kiri,
            text="Hapus Foto",
            command=lambda: _hapus_foto(parent, refresh),
            bg=WARNA_KARTU,
            fg=WARNA_TEKS,
            relief="flat",
            cursor="hand2",
        ).pack(fill="x")

    kanan = tk.Frame(kartu, bg=WARNA_KARTU)
    kanan.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 20),
        pady=20,
    )

    tk.Label(
        kanan,
        text=_nilai(data, "nama_lengkap"),
        font=("Segoe UI", 17, "bold"),
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w")

    tk.Label(
        kanan,
        text="Administrator",
        font=FONT_NORMAL,
        fg=WARNA_SEKUNDER,
        bg=WARNA_KARTU,
    ).pack(anchor="w", pady=(3, 15))

    info = tk.Frame(kanan, bg=WARNA_KARTU)
    info.pack(fill="x")

    _buat_label_info(info, "Username", _nilai(data, "username"), 0)
    _buat_label_info(info, "Email", _nilai(data, "email"), 1)
    _buat_label_info(info, "Status Akun", _nilai(data, "is_active"), 2)
    _buat_label_info(info, "Dibuat", _nilai(data, "created_at"), 3)
    _buat_label_info(info, "Login Terakhir", _nilai(data, "last_login_at"), 4)

    kartu_password = _buat_kartu(parent)
    kartu_password.pack(fill="x", padx=20, pady=(0, 15))

    tk.Label(
        kartu_password,
        text="Keamanan Akun",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w", padx=20, pady=(20, 5))

    tk.Button(
        kartu_password,
        text="Ganti Password",
        command=lambda: _dialog_ganti_password(parent),
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
    ).pack(anchor="w", padx=20, pady=15)

    _tampilkan_pengajuan_admin(parent, refresh)


# ============================================================
# ADMIN - PENGAJUAN NIM
# ============================================================

def _tampilkan_pengajuan_admin(parent, refresh):
    """Menampilkan daftar pengajuan perubahan NIM."""

    kartu = _buat_kartu(parent)
    kartu.pack(fill="x", padx=20, pady=(0, 20))

    tk.Label(
        kartu,
        text="Pengajuan Perubahan NIM",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w", padx=20, pady=(20, 5))

    data = profile.daftar_pengajuan_nim()

    if not data:
        tk.Label(
            kartu,
            text="Belum ada pengajuan perubahan NIM.",
            font=FONT_KETERANGAN,
            fg=WARNA_SEKUNDER,
            bg=WARNA_KARTU,
        ).pack(anchor="w", padx=20, pady=(0, 20))
        return

    for item in data:
        frame = tk.Frame(
            kartu,
            bg=WARNA_KARTU,
            highlightbackground=WARNA_BORDER,
            highlightthickness=1,
        )
        frame.pack(fill="x", padx=20, pady=(5, 10))

        teks = (
            f"{item['nim_lama']} → {item['nim_baru']}\n"
            f"Mahasiswa: {item['nama_lengkap']}\n"
            f"Alasan: {item['alasan']}\n"
            f"Status: {item['status']}"
        )

        if item.get("catatan_admin"):
            teks += f"\nCatatan: {item['catatan_admin']}"

        tk.Label(
            frame,
            text=teks,
            font=FONT_KETERANGAN,
            fg=WARNA_TEKS,
            bg=WARNA_KARTU,
            justify="left",
            anchor="w",
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=12,
        )

        if item["status"] == "Menunggu":
            tombol = tk.Frame(frame, bg=WARNA_KARTU)
            tombol.pack(side="right", padx=15)

            tk.Button(
                tombol,
                text="Setujui",
                command=lambda pid=item["pengajuan_id"]: (
                    _setujui_nim(parent, pid, refresh)
                ),
                bg=WARNA_UTAMA,
                fg="white",
                relief="flat",
                cursor="hand2",
            ).pack(fill="x", pady=(0, 5))

            tk.Button(
                tombol,
                text="Tolak",
                command=lambda pid=item["pengajuan_id"]: (
                    _tolak_nim(parent, pid, refresh)
                ),
                bg=WARNA_KARTU,
                fg=WARNA_TEKS,
                relief="flat",
                cursor="hand2",
            ).pack(fill="x")


def _setujui_nim(parent, pengajuan_id, refresh):
    """Menyetujui pengajuan NIM."""

    if not messagebox.askyesno(
        "Setujui Pengajuan",
        "Yakin ingin menyetujui pengajuan perubahan NIM ini?",
        parent=parent,
    ):
        return

    try:
        profile.setujui_pengajuan_nim(pengajuan_id)

        messagebox.showinfo(
            "Berhasil",
            "Pengajuan perubahan NIM berhasil disetujui.",
            parent=parent,
        )

        refresh()

    except AppError as exc:
        messagebox.showerror(
            "Gagal",
            str(exc),
            parent=parent,
        )

    except Exception as exc:
        messagebox.showerror(
            "Gagal",
            f"Pengajuan gagal diproses.\n\n{exc}",
            parent=parent,
        )


def _tolak_nim(parent, pengajuan_id, refresh):
    """Menolak pengajuan NIM."""

    dialog = tk.Toplevel(parent)
    dialog.title("Tolak Pengajuan")
    dialog.configure(bg=c.BG_COLOR)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    frame = tk.Frame(
        dialog,
        bg=WARNA_KARTU,
        padx=25,
        pady=25,
    )
    frame.pack(padx=20, pady=20)

    tk.Label(
        frame,
        text="Catatan Admin",
        font=FONT_SUBJUDUL,
        fg=WARNA_TEKS,
        bg=WARNA_KARTU,
    ).pack(anchor="w", pady=(0, 10))

    catatan = tk.Text(
        frame,
        width=40,
        height=5,
        font=FONT_NORMAL,
    )
    catatan.pack()

    def simpan():
        try:
            profile.tolak_pengajuan_nim(
                pengajuan_id,
                catatan.get("1.0", "end"),
            )

            messagebox.showinfo(
                "Berhasil",
                "Pengajuan perubahan NIM ditolak.",
                parent=dialog,
            )

            dialog.destroy()
            refresh()

        except AppError as exc:
            messagebox.showerror(
                "Gagal",
                str(exc),
                parent=dialog,
            )

        except Exception as exc:
            messagebox.showerror(
                "Gagal",
                f"Pengajuan gagal diproses.\n\n{exc}",
                parent=dialog,
            )

    tk.Button(
        frame,
        text="Tolak Pengajuan",
        command=simpan,
        bg=WARNA_UTAMA,
        fg="white",
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
    ).pack(anchor="e", pady=(15, 0))


# ============================================================
# HALAMAN UTAMA PROFILE
# ============================================================

def tampilkan_profile(parent):
    """Menampilkan halaman profil sesuai role pengguna."""

    _bersihkan(parent)

    pengguna = session.get_user()

    if not pengguna:
        tk.Label(
            parent,
            text="Sesi pengguna tidak ditemukan.",
            font=FONT_NORMAL,
            fg=WARNA_TEKS,
            bg=c.BG_COLOR,
        ).pack(pady=50)
        return

    role = pengguna.get("role")

    if role == "mahasiswa":
        ambil_data = profile.profil_mahasiswa
    elif role == "dosen":
        ambil_data = profile.profil_dosen
    elif role == "admin":
        ambil_data = profile.profil_admin
    else:
        raise AppError("Role pengguna tidak dikenal.")

    try:
        data = ambil_data()
    except AppError as exc:
        tk.Label(
            parent,
            text=str(exc),
            font=FONT_NORMAL,
            fg=WARNA_TEKS,
            bg=c.BG_COLOR,
        ).pack(pady=50)
        return
    except Exception as exc:
        tk.Label(
            parent,
            text=f"Profil gagal dimuat.\n\n{exc}",
            font=FONT_NORMAL,
            fg=WARNA_TEKS,
            bg=c.BG_COLOR,
            justify="center",
        ).pack(pady=50)
        return

    refresh = lambda: tampilkan_profile(parent)

    header = tk.Frame(
        parent,
        bg=c.BG_COLOR,
    )
    header.pack(fill="x", padx=20, pady=(20, 15))

    tk.Label(
        header,
        text="Profil",
        font=FONT_JUDUL,
        fg=WARNA_TEKS,
        bg=c.BG_COLOR,
    ).pack(side="left")

    tk.Label(
        header,
        text=f"Akun {_nilai(data, 'nama_lengkap')}",
        font=FONT_NORMAL,
        fg=WARNA_SEKUNDER,
        bg=c.BG_COLOR,
    ).pack(side="left", padx=(15, 0), pady=(7, 0))

    container = tk.Frame(
        parent,
        bg=c.BG_COLOR,
    )
    container.pack(fill="both", expand=True)

    if role == "mahasiswa":
        _tampilkan_mahasiswa(container, data, refresh)

    elif role == "dosen":
        _tampilkan_dosen(container, data, refresh)

    elif role == "admin":
        _tampilkan_admin(container, data, refresh)