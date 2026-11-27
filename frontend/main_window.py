"""Kerangka aplikasi SIAKAD: tema, navigasi, dan menu sesuai role.

Tema: Akademik — bersih, terstruktur, dan nyaman dibaca.

Fitur:
- Sidebar dengan ikon dan indikator menu aktif.
- Header profil pengguna dan tombol keluar.
- Beranda dengan statistik akademik.
- Navigasi halaman berdasarkan role pengguna.
- Pemeriksaan sesi login secara berkala.
"""

import importlib
import tkinter as tk
import traceback
from datetime import date
from tkinter import messagebox, ttk

import mysql.connector

from assets import colors as c
from assets.styles import terapkan_style
from backend import auth, dashboard, ipk as backend_ipk, tugas as backend_tugas
from frontend import login_page
from utils import permissions, session
from utils.validators import AppError


JUDUL = "SIAKAD - Nilai & IPK"
CEK_SESI_MS = 30_000
_TEKS_TERANG = getattr(c, "TEXT_ON_PRIMARY", "#FFFFFF")


# ================================================================
# KONFIGURASI MENU
# ================================================================

MENU = {
    "dashboard": "Beranda",
    "nilai": "Nilai Mahasiswa",
    "transkrip": "Transkrip & IPK",
    "agenda_tugas": "Agenda Tugas",
    "mahasiswa": "Data Mahasiswa",
    "akademik_master": "Master Akademik",
    "dosen": "Data Dosen",
    "kelas": "Kelas Kuliah",
}

MENU_IKON = {
    "dashboard": "🏠",
    "nilai": "📝",
    "transkrip": "📜",
    "agenda_tugas": "📅",
    "mahasiswa": "👥",
    "akademik_master": "🏫",
    "dosen": "👨‍🏫",
    "kelas": "🚪",
}

HALAMAN = {
    "mahasiswa": (
        "frontend.mahasiswa_page",
        "tampilkan_mahasiswa",
        False,
    ),
    "akademik_master": (
        "frontend.akademik_master_page",
        "tampilkan_master",
        False,
    ),
    "dosen": (
        "frontend.dosen_page",
        "tampilkan_dosen",
        False,
    ),
    "kelas": (
        "frontend.kelas_page",
        "tampilkan_kelas",
        False,
    ),
    "agenda_tugas": (
        "frontend.tugas_page",
        "tampilkan_tugas",
        True,
    ),
    "nilai": (
        "frontend.nilai_page",
        "tampilkan_nilai",
        True,
    ),
    "transkrip": (
        "frontend.transkrip_page",
        "tampilkan_transkrip",
        True,
    ),
}

NAMA_ROLE = {
    "admin": "Administrator",
    "dosen": "Dosen",
    "mahasiswa": "Mahasiswa",
}

_state = {
    "after_id": None,
}


# ================================================================
# JENDELA DAN TEMA
# ================================================================

def _tengahkan(root, lebar, tinggi):
    """Menempatkan jendela aplikasi di tengah layar."""

    x = max((root.winfo_screenwidth() - lebar) // 2, 0)
    y = max((root.winfo_screenheight() - tinggi) // 2 - 20, 0)

    root.geometry(f"{lebar}x{tinggi}+{x}+{y}")


def terapkan_tema(root):
    """Menyeragamkan tampilan widget ttk."""

    gaya = ttk.Style(root)
    gaya.theme_use("clam")

    root.option_add("*TCombobox*Listbox.font", c.FONT_BODY)

    gaya.configure(
        ".",
        font=c.FONT_BODY,
        background=c.CARD_BG,
        foreground=c.TEXT_DARK,
    )

    kolom = {
        "padding": (10, 8),
        "fieldbackground": c.CARD_BG,
        "foreground": c.TEXT_DARK,
        "bordercolor": c.BORDER_COLOR,
        "lightcolor": c.BORDER_COLOR,
        "darkcolor": c.BORDER_COLOR,
    }

    fokus = {
        "bordercolor": [("focus", c.PRIMARY_COLOR)],
        "lightcolor": [("focus", c.PRIMARY_COLOR)],
        "darkcolor": [("focus", c.PRIMARY_COLOR)],
    }

    gaya.configure("Form.TEntry", **kolom)
    gaya.map("Form.TEntry", **fokus)

    gaya.configure(
        "Form.TCombobox",
        arrowcolor=c.TEXT_MUTED,
        background=c.CARD_BG,
        **kolom,
    )

    gaya.map(
        "Form.TCombobox",
        fieldbackground=[
            ("readonly", c.CARD_BG),
            ("disabled", c.BG_COLOR),
        ],
        selectbackground=[
            ("readonly", c.CARD_BG),
        ],
        selectforeground=[
            ("readonly", c.TEXT_DARK),
        ],
        foreground=[
            ("disabled", c.TEXT_MUTED),
        ],
        **fokus,
    )

    gaya.configure(
        "Form.TCheckbutton",
        background=c.CARD_BG,
        foreground=c.TEXT_MUTED,
    )

    # Tombol utama
    gaya.configure(
        "Primary.TButton",
        background=c.PRIMARY_COLOR,
        foreground=_TEKS_TERANG,
        font=c.FONT_BUTTON,
        padding=(16, 11),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    gaya.map(
        "Primary.TButton",
        background=[
            ("disabled", c.SURFACE_MUTED),
            ("pressed", c.PRIMARY_DARK),
            ("active", c.PRIMARY_HOVER),
        ],
        foreground=[
            ("disabled", c.TEXT_MUTED),
        ],
    )

    # Tombol sekunder
    gaya.configure(
        "Secondary.TButton",
        background=c.CARD_BG,
        foreground=c.TEXT_DARK,
        font=c.FONT_BUTTON,
        padding=(16, 11),
        bordercolor=c.BORDER_COLOR,
        focusthickness=0,
        relief="flat",
    )

    gaya.map(
        "Secondary.TButton",
        background=[
            ("active", c.SURFACE_MUTED),
        ],
    )

    # Tombol link
    gaya.configure(
        "Link.TButton",
        background=c.CARD_BG,
        foreground=c.PRIMARY_COLOR,
        font=c.FONT_LINK,
        borderwidth=0,
        padding=(0, 2),
        focusthickness=0,
        relief="flat",
    )

    gaya.map(
        "Link.TButton",
        foreground=[
            ("disabled", c.TEXT_MUTED),
            ("active", c.PRIMARY_HOVER),
        ],
        background=[
            ("active", c.CARD_BG),
        ],
    )

    # Tabel
    gaya.configure(
        "Treeview",
        background=c.CARD_BG,
        fieldbackground=c.CARD_BG,
        foreground=c.TEXT_DARK,
        rowheight=32,
        bordercolor=c.BORDER_COLOR,
        borderwidth=0,
    )

    gaya.map(
        "Treeview",
        background=[
            ("selected", c.PRIMARY_LIGHT),
        ],
        foreground=[
            ("selected", c.TEXT_DARK),
        ],
    )

    gaya.configure(
        "Treeview.Heading",
        background=c.PRIMARY_DARK,
        foreground=_TEKS_TERANG,
        font=c.FONT_BOLD,
        padding=(8, 8),
        relief="flat",
    )

    gaya.map(
        "Treeview.Heading",
        background=[
            ("active", c.PRIMARY_HOVER),
        ],
    )

    # Notebook
    gaya.configure(
        "TNotebook",
        background=c.BG_COLOR,
        borderwidth=0,
        tabmargins=(0, 8, 0, 0),
    )

    gaya.configure(
        "TNotebook.Tab",
        background=c.TAB_IDLE_BG,
        foreground=c.TEXT_MUTED,
        padding=(14, 9),
        font=c.FONT_BOLD,
    )

    gaya.map(
        "TNotebook.Tab",
        background=[
            ("selected", c.CARD_BG),
            ("active", c.PRIMARY_LIGHT),
        ],
        foreground=[
            ("selected", c.PRIMARY_DARK),
            ("active", c.TEXT_DARK),
        ],
    )


def mulai(root):
    """Menginisialisasi jendela utama aplikasi."""

    root.title(JUDUL)
    root.configure(bg=c.BG_COLOR)
    root.minsize(980, 620)

    _tengahkan(root, 1100, 700)

    terapkan_style(root)
    terapkan_tema(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: _tutup(root),
    )

    tampilkan_login(root)


def _tutup(root):
    """Menutup aplikasi dan mengakhiri sesi."""

    auth.logout()
    root.destroy()


def _bersihkan(root):
    """Menghapus seluruh widget dan timer sesi sebelumnya."""

    if _state["after_id"] is not None:
        try:
            root.after_cancel(_state["after_id"])
        except tk.TclError:
            pass

        _state["after_id"] = None

    root.unbind("<Return>")

    for anak in root.winfo_children():
        anak.destroy()


# ================================================================
# NAVIGASI DAN SESI
# ================================================================

def tampilkan_login(root, pesan=None, jenis="info"):
    """Menampilkan halaman login."""

    _bersihkan(root)

    return login_page.tampilkan_login(
        root,
        setelah_login=lambda pengguna: tampilkan_aplikasi(
            root,
            pengguna,
        ),
        pesan_awal=(pesan, jenis) if pesan else None,
    )


def keluar(root):
    """Keluar dari akun pengguna."""

    if not messagebox.askyesno(
        "Keluar",
        "Yakin ingin keluar dari aplikasi?",
        parent=root,
    ):
        return

    auth.logout()
    tampilkan_login(root, "Anda telah keluar.", "info")


def _cek_sesi(root):
    """Memeriksa apakah sesi pengguna masih aktif."""

    _state["after_id"] = None

    if not session.is_logged_in():
        auth.logout()

        tampilkan_login(
            root,
            "Sesi Anda telah berakhir. Silakan masuk kembali.",
            "info",
        )
        return

    _state["after_id"] = root.after(
        CEK_SESI_MS,
        lambda: _cek_sesi(root),
    )


def _halaman_pengganti(
    parent,
    judul,
    pesan,
    warna=c.TEXT_MUTED,
):
    """Menampilkan halaman pengganti jika halaman gagal dimuat."""

    kartu = tk.Frame(
        parent,
        bg=c.CARD_BG,
        padx=28,
        pady=24,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
    )

    tk.Label(
        kartu,
        text=judul,
        font=c.FONT_HEADING,
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
    ).pack(anchor="w")

    tk.Label(
        kartu,
        text=pesan,
        font=c.FONT_BODY,
        bg=c.CARD_BG,
        fg=warna,
        wraplength=620,
        justify="left",
        anchor="w",
    ).pack(
        anchor="w",
        pady=(8, 0),
    )

    return kartu


# ================================================================
# BERANDA
# ================================================================

def _buat_beranda(parent, pengguna):
    """Membuat halaman beranda sesuai role pengguna."""

    halaman = tk.Frame(
        parent,
        bg=c.BG_COLOR,
    )

    role_pengguna = pengguna.get("role")

    # ------------------------------------------------------------
    # BERANDA MAHASISWA
    # ------------------------------------------------------------

    if role_pengguna == "mahasiswa":

        try:
            data_akademik = backend_ipk.ringkasan()
        except (AppError, mysql.connector.Error):
            data_akademik = None

        try:
            tugas_hari_ini = backend_tugas.daftar_tanggal(
                date.today()
            )
            pesan_tugas = ""

        except (AppError, mysql.connector.Error):
            tugas_hari_ini = None
            pesan_tugas = "Agenda belum diaktifkan."

        profil = (
            data_akademik.get("profil", {})
            if data_akademik
            else {}
        )

        # Hero card
        hero = tk.Frame(
            halaman,
            bg=c.PRIMARY_DARK,
            padx=36,
            pady=32,
        )

        hero.pack(
            fill="x",
            pady=(0, 24),
        )

        tk.Label(
            hero,
            text=f"Selamat datang, {pengguna.get('nama', 'Mahasiswa')}!",
            font=(c.FONT_FAMILY, 26, "bold"),
            bg=c.PRIMARY_DARK,
            fg=_TEKS_TERANG,
        ).pack(anchor="w")

        identitas = f"NIM {pengguna.get('nim') or '-'}"

        if profil.get("nama_prodi"):
            identitas += f"  •  {profil['nama_prodi']}"

        if profil.get("angkatan"):
            identitas += f"  •  Angkatan {profil['angkatan']}"

        tk.Label(
            hero,
            text=identitas,
            font=(c.FONT_FAMILY, 12),
            bg=c.PRIMARY_DARK,
            fg=c.PRIMARY_LIGHT,
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        # Statistik akademik
        ringkasan = tk.Frame(
            halaman,
            bg=c.BG_COLOR,
        )

        ringkasan.pack(fill="x")

        nilai_akademik = (
            (data_akademik or {}).get("ipk") or {}
        )

        riwayat_ips = (
            (data_akademik or {}).get("ips", [])
        )

        ips_terakhir = (
            riwayat_ips[-1]
            if riwayat_ips
            else None
        )

        statistik = (
            (
                "⭐",
                "IPK",
                nilai_akademik.get("ipk", "-"),
            ),
            (
                "📚",
                "SKS Lulus",
                nilai_akademik.get("total_sks_lulus", 0),
            ),
            (
                "📈",
                (
                    f"IPS {ips_terakhir['kode_semester']}"
                    if ips_terakhir
                    else "IPS"
                ),
                (
                    ips_terakhir.get("ips", "-")
                    if ips_terakhir
                    else "-"
                ),
            ),
        )

        for kolom, (ikon, label, nilai) in enumerate(statistik):

            ringkasan.columnconfigure(
                kolom,
                weight=1,
                uniform="statistik_mahasiswa",
            )

            kartu_stat = tk.Frame(
                ringkasan,
                bg=c.CARD_BG,
                highlightthickness=1,
                highlightbackground=c.BORDER_COLOR,
            )

            kartu_stat.grid(
                row=0,
                column=kolom,
                sticky="nsew",
                padx=(
                    0 if kolom == 0 else 8,
                    0 if kolom == 2 else 8,
                ),
            )

            tk.Frame(
                kartu_stat,
                bg=c.PRIMARY_ACCENT,
                height=4,
            ).pack(fill="x")

            isi_stat = tk.Frame(
                kartu_stat,
                bg=c.CARD_BG,
                padx=22,
                pady=18,
            )

            isi_stat.pack(
                fill="both",
                expand=True,
            )

            header_stat = tk.Frame(
                isi_stat,
                bg=c.CARD_BG,
            )

            header_stat.pack(fill="x")

            tk.Label(
                header_stat,
                text=ikon,
                bg=c.CARD_BG,
                font=(c.FONT_FAMILY, 16),
            ).pack(side="left")

            tk.Label(
                header_stat,
                text=label,
                bg=c.CARD_BG,
                fg=c.TEXT_MUTED,
                font=c.FONT_BOLD,
            ).pack(
                side="left",
                padx=(8, 0),
            )

            tk.Label(
                isi_stat,
                text=str(nilai if nilai is not None else "-"),
                bg=c.CARD_BG,
                fg=c.PRIMARY_DARK,
                font=(c.FONT_FAMILY, 28, "bold"),
            ).pack(
                anchor="w",
                pady=(12, 0),
            )

        # Agenda tugas
        kartu_tugas = tk.Frame(
            halaman,
            bg=c.CARD_BG,
            padx=28,
            pady=24,
            highlightthickness=1,
            highlightbackground=c.BORDER_COLOR,
        )

        kartu_tugas.pack(
            fill="x",
            pady=(24, 0),
        )

        head_tugas = tk.Frame(
            kartu_tugas,
            bg=c.CARD_BG,
        )

        head_tugas.pack(
            fill="x",
            pady=(0, 16),
        )

        tk.Label(
            head_tugas,
            text="📅 Agenda Hari Ini",
            bg=c.CARD_BG,
            fg=c.TEXT_DARK,
            font=(c.FONT_FAMILY, 16, "bold"),
        ).pack(side="left")

        if tugas_hari_ini is None:

            tk.Label(
                kartu_tugas,
                text=pesan_tugas,
                bg=c.CARD_BG,
                fg=c.TEXT_MUTED,
                font=c.FONT_BODY,
                wraplength=900,
                justify="left",
            ).pack(anchor="w")

        elif tugas_hari_ini:

            for item in tugas_hari_ini[:5]:

                baris = tk.Frame(
                    kartu_tugas,
                    bg=c.CARD_BG,
                )

                baris.pack(
                    fill="x",
                    pady=6,
                )

                is_selesai = item["selesai"]

                bg_pill = (
                    c.SUCCESS_BG
                    if is_selesai
                    else c.DANGER_BG
                )

                fg_pill = (
                    c.SUCCESS_COLOR
                    if is_selesai
                    else c.DANGER_COLOR
                )

                teks_pill = (
                    "✓ Selesai"
                    if is_selesai
                    else "⏳ Belum"
                )

                tk.Label(
                    baris,
                    text=teks_pill,
                    bg=bg_pill,
                    fg=fg_pill,
                    font=(c.FONT_FAMILY, 9, "bold"),
                    padx=8,
                    pady=3,
                ).pack(side="left")

                tk.Label(
                    baris,
                    text=item["judul"],
                    bg=c.CARD_BG,
                    fg=(
                        c.TEXT_MUTED
                        if is_selesai
                        else c.TEXT_DARK
                    ),
                    font=(c.FONT_FAMILY, 11),
                ).pack(
                    side="left",
                    padx=14,
                )

        else:

            tk.Label(
                kartu_tugas,
                text="Tidak ada jadwal tugas untuk hari ini.",
                bg=c.CARD_BG,
                fg=c.TEXT_MUTED,
                font=c.FONT_BODY,
            ).pack(anchor="w")

        return halaman

    # ------------------------------------------------------------
    # BERANDA ADMIN DAN DOSEN
    # ------------------------------------------------------------

    hero = tk.Frame(
        halaman,
        bg=c.PRIMARY_DARK,
        padx=36,
        pady=32,
    )

    hero.pack(
        fill="x",
        pady=(0, 24),
    )

    tk.Label(
        hero,
        text=f"Selamat datang, {pengguna.get('nama', 'Pengguna')}!",
        font=(c.FONT_FAMILY, 26, "bold"),
        bg=c.PRIMARY_DARK,
        fg=_TEKS_TERANG,
    ).pack(anchor="w")

    role = NAMA_ROLE.get(
        role_pengguna,
        "Pengguna",
    )

    subjudul = (
        "Pemantauan nilai akhir dan IPK mahasiswa"
        if role_pengguna == "admin"
        else f"{role}  •  Ringkasan aktivitas akademik"
    )

    tk.Label(
        hero,
        text=subjudul,
        font=(c.FONT_FAMILY, 12),
        bg=c.PRIMARY_DARK,
        fg=c.PRIMARY_LIGHT,
    ).pack(
        anchor="w",
        pady=(8, 0),
    )

    try:
        data = dashboard.ringkasan()

    except Exception as err:
        traceback.print_exc()

        _halaman_pengganti(
            halaman,
            "Ringkasan belum tersedia",
            f"Data dashboard tidak dapat dimuat:\n{err}",
            c.DANGER_COLOR,
        ).pack(fill="x")

        return halaman

    ringkasan = tk.Frame(
        halaman,
        bg=c.BG_COLOR,
    )

    ringkasan.pack(fill="x")

    if role_pengguna == "admin":

        statistik = (
            (
                "🎓",
                "Mhs dgn IPK",
                data.get("mahasiswa_dengan_ipk", 0),
            ),
            (
                "📝",
                "Nilai final",
                data.get("jumlah_nilai_final", 0),
            ),
            (
                "🏆",
                "Rata-rata IPK",
                data.get("ipk_rata_rata") or "-",
            ),
            (
                "🗓️",
                "Smt aktif",
                data.get("semester_aktif") or "-",
            ),
        )

    else:

        statistik = (
            (
                "👥",
                "Mahasiswa",
                data.get("jumlah_mahasiswa", 0),
            ),
            (
                "👨‍🏫",
                "Dosen aktif",
                data.get("jumlah_dosen_aktif", 0),
            ),
            (
                "🏫",
                "Program studi",
                data.get("jumlah_prodi", 0),
            ),
            (
                "🗓️",
                "Semester aktif",
                data.get("semester_aktif") or "-",
            ),
        )

    for kolom, (ikon, label, nilai) in enumerate(statistik):

        ringkasan.columnconfigure(
            kolom,
            weight=1,
            uniform="statistik",
        )

        kartu = tk.Frame(
            ringkasan,
            bg=c.CARD_BG,
            highlightthickness=1,
            highlightbackground=c.BORDER_COLOR,
        )

        kartu.grid(
            row=0,
            column=kolom,
            sticky="nsew",
            padx=(
                0 if kolom == 0 else 8,
                0 if kolom == 3 else 8,
            ),
        )

        tk.Frame(
            kartu,
            bg=c.PRIMARY_ACCENT,
            height=4,
        ).pack(fill="x")

        isi_kartu = tk.Frame(
            kartu,
            bg=c.CARD_BG,
            padx=20,
            pady=18,
        )

        isi_kartu.pack(
            fill="both",
            expand=True,
        )

        header_kartu = tk.Frame(
            isi_kartu,
            bg=c.CARD_BG,
        )

        header_kartu.pack(fill="x")

        tk.Label(
            header_kartu,
            text=ikon,
            bg=c.CARD_BG,
            font=(c.FONT_FAMILY, 16),
        ).pack(side="left")

        tk.Label(
            header_kartu,
            text=label,
            bg=c.CARD_BG,
            fg=c.TEXT_MUTED,
            font=c.FONT_BOLD,
        ).pack(
            side="left",
            padx=(8, 0),
        )

        tk.Label(
            isi_kartu,
            text=str(nilai),
            bg=c.CARD_BG,
            fg=c.PRIMARY_DARK,
            font=(c.FONT_FAMILY, 24, "bold"),
        ).pack(
            anchor="w",
            pady=(12, 0),
        )

    return halaman


# ================================================================
# PEMUAT HALAMAN
# ================================================================

def _buat_halaman(kunci, parent, pengguna):
    """Memuat halaman berdasarkan kunci menu."""

    label = MENU[kunci]

    if kunci == "dashboard":
        return _buat_beranda(parent, pengguna)

    nama_modul, nama_fungsi, pakai_user = HALAMAN[kunci]

    try:
        modul = importlib.import_module(nama_modul)
        fungsi = getattr(modul, nama_fungsi)

        if pakai_user:
            return fungsi(parent, pengguna)

        return fungsi(parent)

    except ModuleNotFoundError as err:

        if err.name == nama_modul:
            return _halaman_pengganti(
                parent,
                label,
                "Halaman ini belum tersedia.",
            )

        traceback.print_exc()

        return _halaman_pengganti(
            parent,
            label,
            f"Gagal memuat halaman: {err}",
            c.DANGER_COLOR,
        )

    except Exception as err:
        traceback.print_exc()

        return _halaman_pengganti(
            parent,
            label,
            f"Halaman tidak dapat dibuka:\n{err}",
            c.DANGER_COLOR,
        )


# ================================================================
# APLIKASI UTAMA
# ================================================================

def tampilkan_aplikasi(root, pengguna):
    """Membuat kerangka utama setelah pengguna berhasil login."""

    _bersihkan(root)

    kerangka = tk.Frame(
        root,
        bg=c.BG_COLOR,
    )

    kerangka.pack(
        fill="both",
        expand=True,
    )

    kerangka.rowconfigure(1, weight=1)
    kerangka.columnconfigure(1, weight=1)

    # ------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------

    header = tk.Frame(
        kerangka,
        bg=c.CARD_BG,
        padx=24,
        pady=16,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
    )

    header.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="ew",
    )

    identitas = tk.Frame(
        header,
        bg=c.CARD_BG,
    )

    identitas.pack(side="left")

    tk.Label(
        identitas,
        text="🎓",
        font=(c.FONT_FAMILY, 18, "bold"),
        bg=c.PRIMARY_DARK,
        fg=_TEKS_TERANG,
        width=3,
        pady=6,
    ).pack(
        side="left",
        padx=(0, 12),
    )

    merek = tk.Frame(
        identitas,
        bg=c.CARD_BG,
    )

    merek.pack(side="left")

    tk.Label(
        merek,
        text="SIAKAD",
        font=(c.FONT_FAMILY, 16, "bold"),
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
    ).pack(anchor="w")

    tk.Label(
        merek,
        text="Sistem Informasi Akademik",
        font=c.FONT_SMALL,
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
    ).pack(anchor="w")

    def keluar_dari_akun():
        konfirmasi = messagebox.askyesno(
            "Keluar",
            "Yakin ingin keluar dari akun?",
            parent=root,
        )

        if konfirmasi:
            auth.logout()
            tampilkan_login(
                root,
                "Anda telah keluar.",
                "info",
            )

    btn_keluar = tk.Button(
        header,
        text="Keluar",
        font=c.FONT_BOLD,
        bg=c.DANGER_BG,
        fg=c.DANGER_COLOR,
        relief="flat",
        bd=0,
        padx=16,
        pady=8,
        cursor="hand2",
        command=keluar_dari_akun,
    )

    btn_keluar.pack(side="right")

    # ------------------------------------------------------------
    # PROFIL PENGGUNA
    # ------------------------------------------------------------

    profil = tk.Frame(
        header,
        bg=c.CARD_BG,
    )

    profil.pack(
        side="right",
        padx=(0, 24),
    )

    nama = pengguna.get(
        "nama",
        "Pengguna",
    )

    inisial = (
        "".join(
            kata[0]
            for kata in nama.split()[:2]
        ).upper()
        or "U"
    )

    kanvas_avatar = tk.Canvas(
        profil,
        width=40,
        height=40,
        bg=c.CARD_BG,
        highlightthickness=0,
    )

    kanvas_avatar.pack(
        side="left",
        padx=(0, 12),
    )

    kanvas_avatar.create_oval(
        2,
        2,
        38,
        38,
        fill=c.PRIMARY_ACCENT,
        outline="",
    )

    kanvas_avatar.create_text(
        20,
        20,
        text=inisial,
        fill=_TEKS_TERANG,
        font=(c.FONT_FAMILY, 12, "bold"),
    )

    teks_profil = tk.Frame(
        profil,
        bg=c.CARD_BG,
    )

    teks_profil.pack(side="left")

    tk.Label(
        teks_profil,
        text=nama,
        font=c.FONT_BOLD,
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
    ).pack(anchor="e")

    keterangan = NAMA_ROLE.get(
        pengguna.get("role"),
        pengguna.get("role", "Pengguna"),
    )

    if pengguna.get("nim"):
        keterangan += f"  •  {pengguna['nim']}"

    tk.Label(
        teks_profil,
        text=keterangan,
        font=c.FONT_SMALL,
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
    ).pack(anchor="e")

    # ------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------

    sidebar = tk.Frame(
        kerangka,
        bg=c.SIDEBAR_BG,
        width=250,
    )

    sidebar.grid(
        row=1,
        column=0,
        sticky="ns",
    )

    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="MENU UTAMA",
        font=(c.FONT_FAMILY, 9, "bold"),
        bg=c.SIDEBAR_BG,
        fg=c.SIDEBAR_TEXT,
        anchor="w",
        padx=24,
    ).pack(
        fill="x",
        pady=(28, 12),
    )

    # ------------------------------------------------------------
    # AREA KONTEN
    # ------------------------------------------------------------

    konten = tk.Frame(
        kerangka,
        bg=c.BG_COLOR,
        padx=32,
        pady=32,
    )

    konten.grid(
        row=1,
        column=1,
        sticky="nsew",
    )

    isi = tk.Frame(
        konten,
        bg=c.BG_COLOR,
    )

    isi.pack(
        fill="both",
        expand=True,
    )

    tombol_menu = {}

    # ------------------------------------------------------------
    # MENGATUR WARNA MENU AKTIF
    # ------------------------------------------------------------

    def warnai(kunci_aktif):

        for kunci, frame_tombol in tombol_menu.items():

            aktif = kunci == kunci_aktif

            anak_widget = frame_tombol.winfo_children()

            ikon = anak_widget[0]
            lbl = anak_widget[1]
            bar = anak_widget[2]

            if aktif:

                frame_tombol.configure(
                    bg=c.SIDEBAR_ACTIVE,
                )

                ikon.configure(
                    bg=c.SIDEBAR_ACTIVE,
                    fg=_TEKS_TERANG,
                )

                lbl.configure(
                    bg=c.SIDEBAR_ACTIVE,
                    fg=_TEKS_TERANG,
                )

                bar.configure(
                    bg=_TEKS_TERANG,
                )

            else:

                frame_tombol.configure(
                    bg=c.SIDEBAR_BG,
                )

                ikon.configure(
                    bg=c.SIDEBAR_BG,
                    fg=c.SIDEBAR_TEXT,
                )

                lbl.configure(
                    bg=c.SIDEBAR_BG,
                    fg=c.SIDEBAR_TEXT,
                )

                bar.configure(
                    bg=c.SIDEBAR_BG,
                )

    # ------------------------------------------------------------
    # MEMBUKA HALAMAN
    # ------------------------------------------------------------

    def buka(kunci):

        if not session.is_logged_in():
            _cek_sesi(root)
            return

        warnai(kunci)

        for anak in isi.winfo_children():
            anak.destroy()

        hasil = _buat_halaman(
            kunci,
            isi,
            pengguna,
        )

        if hasil is not None:
            hasil.pack(
                fill="both",
                expand=True,
            )

    # ------------------------------------------------------------
    # MEMBUAT MENU SESUAI ROLE
    # ------------------------------------------------------------

    kunci_menu = [
        kunci
        for kunci in permissions.menus_for_current_user()
        if kunci in MENU
    ]

    for kunci in kunci_menu:

        frame_tombol = tk.Frame(
            sidebar,
            bg=c.SIDEBAR_BG,
            cursor="hand2",
        )

        frame_tombol.pack(fill="x")

        lbl_ikon = tk.Label(
            frame_tombol,
            text=MENU_IKON.get(kunci, "•"),
            font=(c.FONT_FAMILY, 12),
            bg=c.SIDEBAR_BG,
            fg=c.SIDEBAR_TEXT,
            padx=20,
            pady=12,
        )

        lbl_ikon.pack(side="left")

        lbl_teks = tk.Label(
            frame_tombol,
            text=MENU[kunci],
            font=c.FONT_BOLD,
            bg=c.SIDEBAR_BG,
            fg=c.SIDEBAR_TEXT,
            anchor="w",
        )

        lbl_teks.pack(
            side="left",
            fill="x",
            expand=True,
        )

        bar = tk.Frame(
            frame_tombol,
            width=4,
            bg=c.SIDEBAR_BG,
        )

        bar.pack(
            side="right",
            fill="y",
        )

        def on_enter(event, f=frame_tombol):
            if f.cget("bg") != c.SIDEBAR_ACTIVE:
                f.configure(bg=c.SIDEBAR_HOVER)
                for widget in f.winfo_children():
                    if widget != f.winfo_children()[2]:
                        widget.configure(bg=c.SIDEBAR_HOVER)

        def on_leave(event, f=frame_tombol):
            if f.cget("bg") != c.SIDEBAR_ACTIVE:
                f.configure(bg=c.SIDEBAR_BG)
                for widget in f.winfo_children():
                    if widget != f.winfo_children()[2]:
                        widget.configure(bg=c.SIDEBAR_BG)

        for widget in (frame_tombol, lbl_ikon, lbl_teks):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda event, k=kunci: buka(k))

        tombol_menu[kunci] = frame_tombol

    buka("dashboard" if "dashboard" in kunci_menu else kunci_menu[0])
    _state["after_id"] = root.after(CEK_SESI_MS, lambda: _cek_sesi(root))
    return kerangka
