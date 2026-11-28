"""Halaman login dan dialog pendaftaran mahasiswa (Tkinter + ttk)."""

import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets import colors as c
from assets.styles import terapkan_style
from backend import auth
from utils.recent_accounts import (
    muat_akun,
    muat_password_admin,
    muat_password_dosen,
    muat_username_admin,
    muat_username_dosen,
    simpan_akun,
    simpan_akun_admin,
    simpan_akun_dosen,
    simpan_username_admin,
    simpan_username_dosen,
    hapus_akun_admin,
    hapus_akun_dosen,
)
from utils.validators import AppError, nim_input_diizinkan


PESAN_DB = (
    "Tidak dapat mengakses database. Pastikan MySQL (Laragon) sudah menyala "
    "dan isi file .env benar.\n\n{err}"
)

_IKON = {
    "error": "✕",
    "sukses": "✓",
    "info": "ℹ",
}

_WARNA = {
    "error": (c.DANGER_COLOR, c.DANGER_BG),
    "sukses": (c.SUCCESS_COLOR, c.SUCCESS_BG),
    "info": (c.INFO_COLOR, c.INFO_BG),
}

# Warna permukaan khusus aksen akademik lembut
_TEKS_TERANG = getattr(c, "TEXT_ON_PRIMARY", "#FFFFFF")
_KARTU_INGAT_AKTIF = getattr(c, "SURFACE_SELECTED", "#E4EFE1")
_KOTAK_INFO_BG = getattr(c, "INFO_BG", "#E3F0F7")
_KOTAK_INFO_BORDER = getattr(c, "INFO_BORDER", "#B8D8EA")
_KOTAK_INFO_FG = getattr(c, "INFO_COLOR", "#1D5B79")
_FOOTER_MUTED = getattr(c, "SIDEBAR_TEXT", "#DCE5D9")


# ======================================================================
# PEMBANTU
# ======================================================================

def _hex_ke_rgb(hex_warna):
    bersih = hex_warna.lstrip("#")
    return tuple(int(bersih[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_ke_hex(r, g, b):
    return (
        f"#{max(0, min(255, r)):02x}"
        f"{max(0, min(255, g)):02x}"
        f"{max(0, min(255, b)):02x}"
    )


def _buat_pesan(parent, latar, lebar=340):
    """Banner pesan dengan ikon & warna status. Disembunyikan saat kosong."""
    luar = tk.Frame(parent, bg=latar)
    kotak = tk.Frame(luar, bg=latar)

    ikon = tk.Label(
        kotak,
        text="",
        bg=latar,
        fg=c.TEXT_DARK,
        font=(c.FONT_FAMILY, 11, "bold"),
        width=3,
    )
    ikon.pack(side="left", padx=(10, 0), fill="y")

    label = tk.Label(
        kotak,
        text="",
        bg=latar,
        fg=c.TEXT_DARK,
        font=c.FONT_SMALL,
        wraplength=lebar,
        justify="left",
        anchor="w",
        padx=6,
        pady=8,
    )
    label.pack(side="left", fill="both", expand=True, padx=(0, 10))

    def tampil(teks="", jenis="error"):
        if not teks:
            kotak.pack_forget()
            return

        warna, bg = _WARNA.get(jenis, _WARNA["error"])

        kotak.configure(bg=bg)
        ikon.configure(
            text=_IKON.get(jenis, "•"),
            fg=warna,
            bg=bg,
        )
        label.configure(
            text=teks,
            fg=warna,
            bg=bg,
        )

        kotak.pack(fill="x")

    return luar, tampil


def _kolom(parent, latar, teks, show=None, lebar=38, nim=False):
    """Label + entry. Focus ring ditangani lewat style Form.TEntry."""
    bungkus = tk.Frame(parent, bg=latar)
    bungkus.pack(fill="x", pady=(0, 18))

    tk.Label(
        bungkus,
        text=teks,
        bg=latar,
        fg=c.TEXT_DARK,
        font=c.FONT_BOLD,
        anchor="w",
    ).pack(fill="x", pady=(0, 8))

    entry = ttk.Entry(
        bungkus,
        width=lebar,
        style="Form.TEntry",
        show=show or "",
    )

    if nim:
        validasi = (
            entry.register(nim_input_diizinkan),
            "%P",
        )
        entry.configure(
            validate="key",
            validatecommand=validasi,
        )

    entry.pack(fill="x")

    return entry


def _kosongkan(entry, isi=""):
    entry.delete(0, "end")

    if isi:
        entry.insert(0, isi)


def _tengahkan(jendela, induk, lebar, tinggi):
    induk.update_idletasks()

    x = (
        induk.winfo_rootx()
        + max((induk.winfo_width() - lebar) // 2, 0)
    )

    y = (
        induk.winfo_rooty()
        + max((induk.winfo_height() - tinggi) // 2, 0)
    )

    jendela.geometry(f"{lebar}x{tinggi}+{x}+{y}")


def _buat_kartu_ingat(parent, judul, keterangan):
    """Kartu pilihan ingat akun dengan kotak centang yang mengikuti tema."""
    pilihan = tk.BooleanVar(master=parent, value=True)

    kartu = tk.Frame(
        parent,
        bg=c.SURFACE_MUTED,
        padx=14,
        pady=12,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
        takefocus=True,
    )
    kartu.pack(fill="x", pady=(0, 14))

    indikator = tk.Canvas(
        kartu,
        width=22,
        height=22,
        bg=c.SURFACE_MUTED,
        highlightthickness=0,
        cursor="hand2",
    )
    indikator.pack(side="left", padx=(0, 11))

    teks = tk.Frame(
        kartu,
        bg=c.SURFACE_MUTED,
        cursor="hand2",
    )
    teks.pack(side="left", fill="x", expand=True)

    label_judul = tk.Label(
        teks,
        text=judul,
        bg=c.SURFACE_MUTED,
        fg=c.TEXT_DARK,
        font=(c.FONT_FAMILY, 12, "bold"),
        anchor="w",
        cursor="hand2",
    )
    label_judul.pack(fill="x")

    label_keterangan = tk.Label(
        teks,
        text=keterangan,
        bg=c.SURFACE_MUTED,
        fg=c.TEXT_MUTED,
        font=(c.FONT_FAMILY, 10),
        anchor="w",
        cursor="hand2",
        justify="left",
        wraplength=520,
    )
    label_keterangan.pack(fill="x", pady=(3, 0))

    def gambar():
        aktif = pilihan.get()

        latar = (
            _KARTU_INGAT_AKTIF
            if aktif
            else c.CARD_BG
        )

        garis = (
            c.PRIMARY_ACCENT
            if aktif
            else c.BORDER_COLOR
        )

        kartu.configure(
            bg=latar,
            highlightbackground=garis,
        )
        teks.configure(bg=latar)
        label_judul.configure(bg=latar)
        label_keterangan.configure(bg=latar)
        indikator.configure(bg=latar)

        indikator.delete("all")

        indikator.create_rectangle(
            2,
            2,
            20,
            20,
            fill=c.PRIMARY_ACCENT if aktif else c.CARD_BG,
            outline=c.PRIMARY_ACCENT if aktif else c.BORDER_COLOR,
            width=2,
        )

        if aktif:
            indikator.create_line(
                5,
                11,
                9,
                15,
                16,
                7,
                fill=_TEKS_TERANG,
                width=2,
                capstyle="round",
                joinstyle="round",
            )

    def toggle(event=None):
        pilihan.set(not pilihan.get())
        gambar()
        kartu.focus_set()
        return "break"

    for widget in (
        kartu,
        indikator,
        teks,
        label_judul,
        label_keterangan,
    ):
        widget.bind("<Button-1>", toggle)
        widget.bind("<space>", toggle)

    gambar()

    return pilihan


def _pasang_saran(root, entry, records, label_key, saat_dipilih):
    """Autocomplete popup hover/ketik untuk satu jenis akun tersimpan."""
    popup = tk.Toplevel(root)
    popup.withdraw()
    popup.overrideredirect(True)
    popup.transient(root)

    daftar = tk.Listbox(
        popup,
        height=5,
        activestyle="none",
        exportselection=False,
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
        selectbackground=c.PRIMARY_ACCENT,
        selectforeground=_TEKS_TERANG,
        font=c.FONT_BODY,
        relief="solid",
        borderwidth=1,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
    )
    daftar.pack(fill="both", expand=True)

    cocok = []

    def tutup():
        popup.withdraw()

    def pointer_di(widget):
        x = root.winfo_pointerx()
        y = root.winfo_pointery()

        kiri = widget.winfo_rootx()
        atas = widget.winfo_rooty()

        return (
            kiri <= x < kiri + widget.winfo_width()
            and atas <= y < atas + widget.winfo_height()
        )

    def pointer_di_area():
        return (
            pointer_di(entry)
            or (
                popup.winfo_viewable()
                and pointer_di(daftar)
            )
        )

    def perbarui(event=None, semua=False):
        if not pointer_di_area():
            tutup()
            return

        teks = entry.get().strip().casefold()

        cocok[:] = [
            record
            for record in records
            if (
                semua
                or not teks
                or teks in str(record[label_key]).casefold()
            )
        ]

        daftar.delete(0, "end")

        for record in cocok:
            daftar.insert("end", record[label_key])

        if not cocok:
            tutup()
            return

        daftar.configure(
            height=min(len(cocok), 5)
        )

        root.update_idletasks()

        x = entry.winfo_rootx()
        y = entry.winfo_rooty() + entry.winfo_height()

        tinggi = daftar.winfo_reqheight() + 2

        if y + tinggi > popup.winfo_screenheight():
            y = entry.winfo_rooty() - tinggi

        popup.geometry(
            f"{entry.winfo_width()}x{tinggi}+{x}+{y}"
        )
        popup.deiconify()
        popup.lift()

    def pilih(event=None):
        pilihan = daftar.curselection()

        if pilihan and pilihan[0] < len(cocok):
            saat_dipilih(cocok[pilihan[0]])

        tutup()
        entry.focus_set()
        entry.icursor("end")

        return "break"

    def sorot(event):
        indeks = daftar.nearest(event.y)

        if 0 <= indeks < len(cocok):
            daftar.selection_clear(0, "end")
            daftar.selection_set(indeks)
            daftar.activate(indeks)

    def hilangkan_sorot(event=None):
        daftar.selection_clear(0, "end")

    def panah_bawah(event=None):
        if popup.winfo_viewable() and cocok:
            daftar.selection_clear(0, "end")
            daftar.selection_set(0)
            daftar.activate(0)
            daftar.focus_set()

            return "break"

    def enter(event=None):
        if popup.winfo_viewable() and cocok:
            if not daftar.curselection():
                daftar.selection_set(0)

            return pilih()

    def escape(event=None):
        tutup()
        entry.focus_set()
        return "break"

    def tutup_jika_fokus_pindah():
        if root.focus_get() not in (entry, daftar):
            tutup()

    def jadwalkan_tutup(event=None):
        root.after(
            120,
            lambda: (
                None
                if pointer_di_area()
                else tutup()
            ),
        )

    def fokus_keluar(event=None):
        root.after(120, tutup_jika_fokus_pindah)

    def ketik(event=None):
        if event.keysym not in (
            "Up",
            "Down",
            "Return",
            "Escape",
            "Tab",
        ):
            perbarui()

    entry.bind(
        "<Enter>",
        lambda event: perbarui(semua=True),
    )
    entry.bind(
        "<Leave>",
        jadwalkan_tutup,
    )
    entry.bind(
        "<KeyRelease>",
        ketik,
    )
    entry.bind(
        "<Down>",
        panah_bawah,
    )
    entry.bind(
        "<Return>",
        enter,
    )
    entry.bind(
        "<Escape>",
        escape,
    )
    entry.bind(
        "<FocusOut>",
        fokus_keluar,
    )

    daftar.bind(
        "<ButtonRelease-1>",
        pilih,
    )
    daftar.bind(
        "<Motion>",
        sorot,
    )
    daftar.bind(
        "<Leave>",
        hilangkan_sorot,
    )
    daftar.bind(
        "<Leave>",
        jadwalkan_tutup,
        add="+",
    )
    daftar.bind(
        "<Return>",
        pilih,
    )
    daftar.bind(
        "<Escape>",
        escape,
    )
    daftar.bind(
        "<FocusOut>",
        fokus_keluar,
    )

    return perbarui, popup


# ======================================================================
# BRAND PANEL
# ======================================================================

def _panel_brand(frame):
    """Panel kiri: gradasi hijau kampus + aksen geometris akademik."""
    kiri = tk.Frame(
        frame,
        bg=c.PRIMARY_GRADIENT_BOT,
    )
    kiri.grid(
        row=0,
        column=0,
        sticky="nsew",
    )

    kanvas = tk.Canvas(
        kiri,
        highlightthickness=0,
        bd=0,
    )
    kanvas.place(
        relwidth=1,
        relheight=1,
    )

    r_top, g_top, b_top = _hex_ke_rgb(
        c.PRIMARY_GRADIENT_TOP
    )
    r_bot, g_bot, b_bot = _hex_ke_rgb(
        c.PRIMARY_GRADIENT_BOT
    )

    def _gambar_gradasi(event=None):
        kanvas.delete("grad")

        w = kanvas.winfo_width() or 1
        h = kanvas.winfo_height() or 1

        langkah = max(h // 40, 1)

        for i in range(0, h, langkah):
            rasio = i / h

            r = int(
                r_top + (r_bot - r_top) * rasio
            )
            g = int(
                g_top + (g_bot - g_top) * rasio
            )
            b = int(
                b_top + (b_bot - b_top) * rasio
            )

            kanvas.create_rectangle(
                0,
                i,
                w,
                i + langkah,
                fill=_rgb_ke_hex(r, g, b),
                outline="",
                tags="grad",
            )

        kanvas.create_oval(
            -140,
            -140,
            260,
            260,
            fill=c.PRIMARY_HOVER,
            outline="",
            stipple="gray50",
            tags="grad",
        )

        kanvas.create_oval(
            w - 180,
            h - 180,
            w + 100,
            h + 100,
            fill=c.PRIMARY_ACCENT,
            outline="",
            stipple="gray25",
            tags="grad",
        )

    kanvas.bind(
        "<Configure>",
        _gambar_gradasi,
    )

    isi = tk.Frame(
        kanvas,
        bg=c.PRIMARY_GRADIENT_TOP,
    )
    isi.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
    )

    badge = tk.Frame(
        isi,
        bg=c.PRIMARY_ACCENT,
        padx=18,
        pady=10,
    )
    badge.pack(
        anchor="w",
        pady=(0, 28),
    )

    tk.Label(
        badge,
        text="🎓",
        font=(c.FONT_FAMILY, 18, "bold"),
        bg=c.PRIMARY_ACCENT,
        fg=_TEKS_TERANG,
    ).pack(
        side="left",
        padx=(0, 9),
    )

    tk.Label(
        badge,
        text="SIAKAD",
        font=(c.FONT_FAMILY, 18, "bold"),
        bg=c.PRIMARY_ACCENT,
        fg=_TEKS_TERANG,
    ).pack(side="left")

    tk.Label(
        isi,
        text="Portal Akademik\nIPK & Penugasan",
        font=(c.FONT_FAMILY, 27, "bold"),
        bg=c.PRIMARY_GRADIENT_TOP,
        fg=_TEKS_TERANG,
        justify="left",
    ).pack(anchor="w")

    tk.Label(
        isi,
        text=(
            "Kelola tugas kuliah, rekap nilai,\n"
            "dan pantau IPS/IPK secara terstruktur."
        ),
        font=(c.FONT_FAMILY, 13),
        bg=c.PRIMARY_GRADIENT_TOP,
        fg=c.PRIMARY_LIGHT,
        justify="left",
    ).pack(
        anchor="w",
        pady=(12, 36),
    )

    for baris in (
        "Monitoring tugas & tenggat kuliah",
        "Kalkulasi IPS & IPK akurat",
        "Akses terpisah Admin, Dosen & Mahasiswa",
    ):
        baris_frame = tk.Frame(
            isi,
            bg=c.PRIMARY_GRADIENT_TOP,
        )
        baris_frame.pack(
            anchor="w",
            pady=7,
        )

        tk.Label(
            baris_frame,
            text="✓",
            font=(c.FONT_FAMILY, 13, "bold"),
            bg=c.PRIMARY_GRADIENT_TOP,
            fg=c.PRIMARY_LIGHT,
            width=2,
            anchor="w",
        ).pack(side="left")

        tk.Label(
            baris_frame,
            text=baris,
            font=(c.FONT_FAMILY, 12),
            bg=c.PRIMARY_GRADIENT_TOP,
            fg=_TEKS_TERANG,
            anchor="w",
        ).pack(side="left")

    tk.Label(
        kiri,
        text="© Sistem Akademik Kampus",
        font=(c.FONT_FAMILY, 10),
        bg=c.PRIMARY_GRADIENT_BOT,
        fg=_FOOTER_MUTED,
    ).place(
        relx=0.5,
        rely=0.96,
        anchor="center",
    )


# ======================================================================
# LOGIN
# ======================================================================

def tampilkan_login(root, setelah_login, pesan_awal=None):
    """Membangun layar login di dalam root dan mengembalikan frame-nya."""
    terapkan_style(root)

    frame = tk.Frame(
        root,
        bg=c.BG_COLOR,
    )
    frame.pack(
        fill="both",
        expand=True,
    )

    frame.rowconfigure(
        0,
        weight=1,
    )

    # Panel kiri sedikit lebih lebar
    frame.columnconfigure(
        0,
        weight=5,
        uniform="panel",
    )
    frame.columnconfigure(
        1,
        weight=7,
        uniform="panel",
    )

    _panel_brand(frame)

    kanan = tk.Frame(
        frame,
        bg=c.BG_COLOR,
    )
    kanan.grid(
        row=0,
        column=1,
        sticky="nsew",
    )

    # --------------------------------------------------------------
    # KARTU LOGIN
    # --------------------------------------------------------------

    kartu = tk.Frame(
        kanan,
        bg=c.CARD_BG,
        padx=64,
        pady=54,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
    )

    kartu.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=700,
    )

    def sesuaikan_lebar_kartu(event):
        kartu.place_configure(
            width=max(
                0,
                min(
                    700,
                    event.width - 60,
                ),
            )
        )

    kanan.bind(
        "<Configure>",
        sesuaikan_lebar_kartu,
    )

    # --------------------------------------------------------------
    # HEADER
    # --------------------------------------------------------------

    tk.Label(
        kartu,
        text="Selamat datang",
        font=(c.FONT_FAMILY, 32, "bold"),
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
    ).pack(anchor="w")

    tk.Label(
        kartu,
        text=(
            "Masuk sesuai peran Anda untuk mengakses "
            "IPK dan penugasan."
        ),
        font=(c.FONT_FAMILY, 14),
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
        wraplength=560,
        justify="left",
        anchor="w",
    ).pack(
        anchor="w",
        pady=(8, 30),
    )

    # --------------------------------------------------------------
    # SEGMENTED CONTROL
    # --------------------------------------------------------------

    bar_tab = tk.Frame(
        kartu,
        bg=c.TAB_IDLE_BG,
        padx=4,
        pady=4,
    )
    bar_tab.pack(
        fill="x",
        pady=(0, 28),
    )

    bar_tab.columnconfigure(
        0,
        weight=1,
        uniform="tab",
    )
    bar_tab.columnconfigure(
        1,
        weight=1,
        uniform="tab",
    )
    bar_tab.columnconfigure(
        2,
        weight=1,
        uniform="tab",
    )

    tombol_tab = {}

    for kolom, (kunci, teks) in enumerate((
        ("mahasiswa", "🎓  Mahasiswa"),
        ("dosen", "📘  Dosen"),
        ("admin", "🏛️  Admin"),
    )):
        tombol_tab[kunci] = tk.Button(
            bar_tab,
            text=teks,
            font=(c.FONT_FAMILY, 13, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=18,
            pady=15,
            command=lambda k=kunci: pilih_tab(k),
        )

        tombol_tab[kunci].grid(
            row=0,
            column=kolom,
            sticky="ew",
        )

    # --------------------------------------------------------------
    # AREA FORM
    # --------------------------------------------------------------

    area = tk.Frame(
        kartu,
        bg=c.CARD_BG,
    )
    area.pack(
        fill="x",
    )

    # ==============================================================
    # FORM MAHASISWA
    # ==============================================================

    form_mhs = tk.Frame(
        area,
        bg=c.CARD_BG,
    )

    tk.Label(
        form_mhs,
        text="Nama lengkap",
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
        font=(c.FONT_FAMILY, 12, "bold"),
        anchor="w",
    ).pack(
        fill="x",
        pady=(0, 8),
    )

    in_nama = ttk.Entry(
        form_mhs,
        width=38,
        style="Form.TEntry",
    )
    in_nama.pack(
        fill="x",
        pady=(0, 18),
    )

    in_nim = _kolom(
        form_mhs,
        c.CARD_BG,
        "NIM (9 digit)",
        lebar=38,
        nim=True,
    )

    var_ingat = _buat_kartu_ingat(
        form_mhs,
        "Ingat akun mahasiswa di perangkat ini",
        "Nama dan NIM disimpan lokal agar login berikutnya lebih cepat.",
    )

    akun_terakhir = muat_akun()

    def pilih_akun_mahasiswa(akun):
        _kosongkan(
            in_nama,
            akun["nama"],
        )
        _kosongkan(
            in_nim,
            akun["nim"],
        )

    saran_mahasiswa, popup_mahasiswa = _pasang_saran(
        root,
        in_nama,
        akun_terakhir,
        "nama",
        pilih_akun_mahasiswa,
    )

    def ingat_akun(nama, nim):
        if not var_ingat.get():
            return

        if simpan_akun(nama, nim):
            akun_terakhir[:] = muat_akun()

            if popup_mahasiswa.winfo_viewable():
                saran_mahasiswa()

    # ==============================================================
    # FORM ADMIN / DOSEN
    # ==============================================================

    form_admin = tk.Frame(
        area,
        bg=c.CARD_BG,
    )

    in_user = _kolom(
        form_admin,
        c.CARD_BG,
        "Username",
        lebar=38,
    )

    bungkus_password = tk.Frame(
        form_admin,
        bg=c.CARD_BG,
    )
    bungkus_password.pack(
        fill="x",
        pady=(0, 18),
    )

    bar_label_password = tk.Frame(
        bungkus_password,
        bg=c.CARD_BG,
    )
    bar_label_password.pack(
        fill="x",
        pady=(0, 8),
    )

    tk.Label(
        bar_label_password,
        text="Password",
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
        font=(c.FONT_FAMILY, 12, "bold"),
        anchor="w",
    ).pack(side="left")

    var_tampil = tk.BooleanVar(
        value=False,
    )

    in_pass = ttk.Entry(
        bungkus_password,
        width=38,
        style="Form.TEntry",
        show="\u2022",
    )
    in_pass.pack(
        fill="x",
    )

    # --------------------------------------------------------------
    # TOMBOL TAMPILKAN PASSWORD
    # --------------------------------------------------------------

    bar_tampil = tk.Frame(
        bungkus_password,
        bg=c.CARD_BG,
        cursor="hand2",
    )
    bar_tampil.pack(
        anchor="w",
        pady=(8, 0),
    )

    ikon_mata = tk.Canvas(
        bar_tampil,
        width=20,
        height=16,
        bg=c.CARD_BG,
        highlightthickness=0,
        cursor="hand2",
    )
    ikon_mata.pack(
        side="left",
        padx=(0, 5),
    )

    tombol_tampil = tk.Button(
        bar_tampil,
        text="Tampilkan password",
        font=(c.FONT_FAMILY, 10),
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
        activebackground=c.CARD_BG,
        activeforeground=c.PRIMARY_ACCENT,
        relief="flat",
        bd=0,
        padx=0,
        pady=1,
        cursor="hand2",
        takefocus=True,
    )
    tombol_tampil.pack(
        side="left",
    )

    petunjuk_password = tk.Label(
        bungkus_password,
        text="",
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
        font=(c.FONT_FAMILY, 10),
        anchor="w",
        justify="left",
        wraplength=520,
    )

    def bersihkan_petunjuk_password(event=None):
        petunjuk_password.pack_forget()

    def gambar_mata():
        warna = (
            c.PRIMARY_ACCENT
            if var_tampil.get()
            else c.TEXT_MUTED
        )

        ikon_mata.delete("all")

        ikon_mata.create_oval(
            1,
            2,
            19,
            14,
            outline=warna,
            width=1.5,
        )

        ikon_mata.create_oval(
            7,
            4,
            13,
            12,
            fill=warna,
            outline=warna,
        )

    def ganti_tampil():
        in_pass.configure(
            show=""
            if var_tampil.get()
            else "\u2022"
        )

        tombol_tampil.configure(
            text=(
                "Sembunyikan password"
                if var_tampil.get()
                else "Tampilkan password"
            ),
            fg=(
                c.PRIMARY_ACCENT
                if var_tampil.get()
                else c.TEXT_MUTED
            ),
        )

        gambar_mata()

    def toggle_tampil(event=None):
        var_tampil.set(
            not var_tampil.get()
        )
        ganti_tampil()
        return "break"

    tombol_tampil.configure(
        command=toggle_tampil,
    )

    bar_tampil.bind(
        "<Button-1>",
        toggle_tampil,
    )

    ikon_mata.bind(
        "<Button-1>",
        toggle_tampil,
    )

    ikon_mata.bind(
        "<Enter>",
        lambda event: tombol_tampil.configure(
            fg=c.PRIMARY_ACCENT
        ),
    )

    ikon_mata.bind(
        "<Leave>",
        lambda event: tombol_tampil.configure(
            fg=(
                c.PRIMARY_ACCENT
                if var_tampil.get()
                else c.TEXT_MUTED
            )
        ),
    )

    tombol_tampil.bind(
        "<Enter>",
        lambda event: tombol_tampil.configure(
            fg=c.PRIMARY_ACCENT
        ),
    )

    tombol_tampil.bind(
        "<Leave>",
        lambda event: tombol_tampil.configure(
            fg=(
                c.PRIMARY_ACCENT
                if var_tampil.get()
                else c.TEXT_MUTED
            )
        ),
    )

    tombol_tampil.bind(
        "<space>",
        toggle_tampil,
    )

    tombol_tampil.bind(
        "<Return>",
        toggle_tampil,
    )

    gambar_mata()

    var_ingat_staff = _buat_kartu_ingat(
        form_admin,
        "Ingat akun di perangkat ini",
        "Username akan disimpan agar login berikutnya lebih mudah.",
    )

    fungsi_akun_staff = {
        "admin": (
            muat_username_admin,
            muat_password_admin,
            simpan_username_admin,
            simpan_akun_admin,
        ),
        "dosen": (
            muat_username_dosen,
            muat_password_dosen,
            simpan_username_dosen,
            simpan_akun_dosen,
        ),
    }

    akun_staff_aktif = []

    fungsi_hapus_akun_staff = {
        "admin": hapus_akun_admin,
        "dosen": hapus_akun_dosen,
    }

    def muat_rekomendasi_staff(role):
        muat_username, muat_password, _, _ = (
            fungsi_akun_staff[role]
        )

        return [
            {
                "username": username,
                "password": muat_password(username),
            }
            for username in muat_username()
        ]

    def pilih_username_staff(akun):
        _kosongkan(
            in_user,
            akun["username"],
        )

        password_tersimpan = akun.get(
            "password",
            "",
        )

        _kosongkan(
            in_pass,
            password_tersimpan,
        )

        if password_tersimpan:
            petunjuk_password.pack_forget()
        else:
            petunjuk_password.configure(
                text=(
                    "Password akun ini belum tersimpan. "
                    "Masukkan password dan login sekali "
                    "dengan opsi ingat akun aktif."
                )
            )

            petunjuk_password.pack(
                anchor="w",
                pady=(6, 0),
            )

    in_pass.bind(
        "<KeyRelease>",
        bersihkan_petunjuk_password,
        add="+",
    )

    saran_staff, popup_staff = _pasang_saran(
        root,
        in_user,
        akun_staff_aktif,
        "username",
        pilih_username_staff,
    )

    def ingat_akun_staff(role, username, password):
        if var_ingat_staff.get():
            (
                _,
                _,
                simpan_username,
                simpan_akun_staff,
            ) = fungsi_akun_staff[role]

            simpan_username(username)
            simpan_akun_staff(
                username,
                password,
            )
        else:
            hapus_akun = fungsi_hapus_akun_staff[
                role
            ]
            hapus_akun(username)

        akun_staff_aktif[:] = (
            muat_rekomendasi_staff(role)
        )

    if popup_staff.winfo_viewable():
        saran_staff()

    # --------------------------------------------------------------
    # PESAN
    # --------------------------------------------------------------

    kotak_pesan, tampil_pesan = _buat_pesan(
        kartu,
        c.CARD_BG,
    )
    kotak_pesan.pack(
        fill="x",
        pady=(10, 8),
    )

    # --------------------------------------------------------------
    # TOMBOL MASUK
    # --------------------------------------------------------------

    tombol_masuk = ttk.Button(
        kartu,
        text="Masuk  →",
        style="Primary.TButton",
    )
    tombol_masuk.pack(
        fill="x",
        pady=(14, 0),
    )

    # --------------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------------

    pemisah = tk.Frame(
        kartu,
        bg=c.CARD_BG,
    )
    pemisah.pack(
        fill="x",
        pady=(30, 0),
    )

    tk.Label(
        pemisah,
        text="Belum punya akun?",
        font=(c.FONT_FAMILY, 11),
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
    ).pack(side="left")

    tombol_daftar = ttk.Button(
        pemisah,
        text="Daftar sebagai mahasiswa",
        style="Link.TButton",
    )
    tombol_daftar.pack(
        side="left",
        padx=(5, 0),
    )

    aktif = {
        "tab": "mahasiswa",
    }

    # --------------------------------------------------------------
    # PILIH TAB
    # --------------------------------------------------------------

    def pilih_tab(kunci, kosongkan_pesan=True):
        role_sebelumnya = aktif["tab"]
        aktif["tab"] = kunci

        popup_mahasiswa.withdraw()
        popup_staff.withdraw()

        if (
            role_sebelumnya != kunci
            and (
                role_sebelumnya in ("admin", "dosen")
                or kunci in ("admin", "dosen")
            )
        ):
            _kosongkan(in_user)
            _kosongkan(in_pass)
            petunjuk_password.pack_forget()

        for k, tombol in tombol_tab.items():
            if k == kunci:
                tombol.configure(
                    bg=c.TAB_ACTIVE_BG,
                    fg=_TEKS_TERANG,
                    activebackground=c.PRIMARY_ACCENT,
                    activeforeground=_TEKS_TERANG,
                )
            else:
                tombol.configure(
                    bg=c.TAB_IDLE_BG,
                    fg=c.TEXT_MUTED,
                    activebackground=c.INPUT_BORDER,
                    activeforeground=c.TEXT_DARK,
                )

        form_mhs.pack_forget()
        form_admin.pack_forget()

        if kunci == "mahasiswa":
            form_mhs.pack(
                fill="x",
            )
            in_nama.focus_set()
        else:
            form_admin.pack(
                fill="x",
            )

            akun_staff_aktif[:] = (
                muat_rekomendasi_staff(kunci)
            )

            in_user.focus_set()

        if kunci == "mahasiswa":
            pemisah.pack(
                fill="x",
                pady=(30, 0),
            )
        else:
            pemisah.pack_forget()

        if kosongkan_pesan:
            tampil_pesan("")

    # --------------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------------

    def masuk(event=None):
        tampil_pesan("")

        try:
            if aktif["tab"] == "mahasiswa":
                pengguna = auth.login_mahasiswa(
                    in_nama.get(),
                    in_nim.get(),
                )

            elif aktif["tab"] == "dosen":
                pengguna = auth.login_dosen(
                    in_user.get(),
                    in_pass.get(),
                )

            else:
                pengguna = auth.login_admin(
                    in_user.get(),
                    in_pass.get(),
                )

        except AppError as err:
            tampil_pesan(
                str(err),
                "error",
            )

            if aktif["tab"] in (
                "admin",
                "dosen",
            ):
                _kosongkan(in_pass)
                in_pass.focus_set()
            else:
                in_nim.focus_set()

            return

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database tidak tersedia",
                PESAN_DB.format(err=err),
                parent=root,
            )
            return

        if aktif["tab"] == "mahasiswa":
            ingat_akun(
                in_nama.get(),
                in_nim.get(),
            )
        else:
            ingat_akun_staff(
                aktif["tab"],
                in_user.get(),
                in_pass.get(),
            )

        root.unbind("<Return>")
        setelah_login(pengguna)

    # --------------------------------------------------------------
    # SETELAH DAFTAR
    # --------------------------------------------------------------

    def setelah_daftar(nim, nama):
        pilih_tab("mahasiswa")

        ingat_akun(
            nama,
            nim,
        )

        _kosongkan(
            in_nama,
            nama,
        )

        _kosongkan(
            in_nim,
            nim,
        )

        tampil_pesan(
            (
                "Pendaftaran berhasil! Klik Masuk, lalu "
                "lengkapi biodata & dosen PA melalui administrator."
            ),
            "sukses",
        )

        tombol_masuk.focus_set()

    tombol_masuk.configure(
        command=masuk,
    )

    tombol_daftar.configure(
        command=lambda: tampilkan_registrasi(
            root,
            setelah_daftar,
        ),
    )

    root.bind(
        "<Return>",
        masuk,
    )

    pilih_tab("mahasiswa")

    if pesan_awal:
        tampil_pesan(*pesan_awal)

    return frame

# ======================================================================
# PENDAFTARAN
# ======================================================================

def tampilkan_registrasi(root, setelah_daftar):
    """Dialog pendaftaran mahasiswa dengan layout 2 kolom yang responsif."""
    terapkan_style(root)

    # --------------------------------------------------------------
    # AMBIL DATA JURUSAN
    # --------------------------------------------------------------

    try:
        jurusan = auth.daftar_jurusan()

    except mysql.connector.Error as err:
        messagebox.showerror(
            "Database tidak tersedia",
            PESAN_DB.format(err=err),
            parent=root,
        )
        return

    if not jurusan:
        messagebox.showinfo(
            "Pendaftaran",
            "Data jurusan belum tersedia. Hubungi administrator.",
            parent=root,
        )
        return

    # --------------------------------------------------------------
    # DIALOG
    # --------------------------------------------------------------

    dialog = tk.Toplevel(root)
    dialog.title("Pendaftaran Mahasiswa Baru")
    dialog.configure(bg=c.BG_COLOR)
    dialog.resizable(False, False)
    dialog.transient(root)

    # Sedikit lebih tinggi agar tombol bawah pasti mendapat ruang.
    # Sebelumnya 900x740 terlalu sempit untuk seluruh isi form.
    _tengahkan(
        dialog,
        root,
        900,
        820,
    )

    # --------------------------------------------------------------
    # KARTU UTAMA
    # --------------------------------------------------------------

    kartu = tk.Frame(
        dialog,
        bg=c.CARD_BG,
        padx=44,
        pady=30,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
    )

    kartu.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20,
    )

    # ==============================================================
    # HEADER
    # ==============================================================

    tk.Label(
        kartu,
        text="Pendaftaran Mahasiswa Baru",
        font=(c.FONT_FAMILY, 24, "bold"),
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
    ).pack(
        anchor="w",
    )

    tk.Label(
        kartu,
        text=(
            "Lengkapi data identitas dan akademik "
            "Anda di bawah ini."
        ),
        font=(c.FONT_FAMILY, 12),
        bg=c.CARD_BG,
        fg=c.TEXT_MUTED,
        justify="left",
    ).pack(
        anchor="w",
        pady=(6, 20),
    )

    # Garis pemisah
    tk.Frame(
        kartu,
        bg=c.BORDER_COLOR,
        height=1,
    ).pack(
        fill="x",
        pady=(0, 20),
    )

    # ==============================================================
    # KONTEN UTAMA 2 KOLOM
    # ==============================================================

    wadah_kolom = tk.Frame(
        kartu,
        bg=c.CARD_BG,
    )

    wadah_kolom.pack(
        fill="x",
    )

    wadah_kolom.columnconfigure(
        0,
        weight=1,
        uniform="kolom",
    )

    wadah_kolom.columnconfigure(
        1,
        weight=1,
        uniform="kolom",
    )

    # ==============================================================
    # KOLOM KIRI — DATA IDENTITAS
    # ==============================================================

    kolom_kiri = tk.Frame(
        wadah_kolom,
        bg=c.CARD_BG,
    )

    kolom_kiri.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 24),
    )

    tk.Label(
        kolom_kiri,
        text="Data Identitas",
        font=(c.FONT_FAMILY, 12, "bold"),
        bg=c.CARD_BG,
        fg=c.PRIMARY_DARK,
    ).pack(
        anchor="w",
        pady=(0, 14),
    )

    # Nama
    in_nama = _kolom(
        kolom_kiri,
        c.CARD_BG,
        "Nama Lengkap",
        lebar=30,
    )

    # NIM
    in_nim = _kolom(
        kolom_kiri,
        c.CARD_BG,
        "NIM (9 digit angka)",
        lebar=30,
        nim=True,
    )

    # --------------------------------------------------------------
    # INFO KEAMANAN
    # --------------------------------------------------------------

    frame_hint = tk.Frame(
        kolom_kiri,
        bg=_KOTAK_INFO_BG,
        padx=14,
        pady=12,
        highlightthickness=1,
        highlightbackground=_KOTAK_INFO_BORDER,
    )

    frame_hint.pack(
        fill="x",
        pady=(4, 0),
    )

    tk.Label(
        frame_hint,
        text="ℹ️   Info Keamanan",
        font=(c.FONT_FAMILY, 10, "bold"),
        bg=_KOTAK_INFO_BG,
        fg=_KOTAK_INFO_FG,
        anchor="w",
    ).pack(
        fill="x",
    )

    tk.Label(
        frame_hint,
        text=(
            "NIM berfungsi sebagai kredensial masuk "
            "mahasiswa. Simpan baik-baik data ini."
        ),
        font=(c.FONT_FAMILY, 10),
        bg=_KOTAK_INFO_BG,
        fg=_KOTAK_INFO_FG,
        justify="left",
        anchor="w",
        wraplength=300,
    ).pack(
        fill="x",
        pady=(5, 0),
    )

    # ==============================================================
    # KOLOM KANAN — DATA AKADEMIK
    # ==============================================================

    kolom_kanan = tk.Frame(
        wadah_kolom,
        bg=c.CARD_BG,
    )

    kolom_kanan.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(24, 0),
    )

    tk.Label(
        kolom_kanan,
        text="Data Akademik",
        font=(c.FONT_FAMILY, 12, "bold"),
        bg=c.CARD_BG,
        fg=c.PRIMARY_DARK,
    ).pack(
        anchor="w",
        pady=(0, 14),
    )

    # --------------------------------------------------------------
    # JURUSAN
    # --------------------------------------------------------------

    tk.Label(
        kolom_kanan,
        text="Jurusan",
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
        font=(c.FONT_FAMILY, 11, "bold"),
        anchor="w",
    ).pack(
        fill="x",
        pady=(0, 7),
    )

    pilih_jurusan = ttk.Combobox(
        kolom_kanan,
        state="readonly",
        style="Form.TCombobox",
        width=30,
    )

    pilih_jurusan["values"] = [
        f"{j['nama_jurusan']} ({j['kode_jurusan']})"
        for j in jurusan
    ]

    pilih_jurusan.pack(
        fill="x",
        pady=(0, 18),
    )

    # --------------------------------------------------------------
    # PROGRAM STUDI
    # --------------------------------------------------------------

    tk.Label(
        kolom_kanan,
        text="Program Studi",
        bg=c.CARD_BG,
        fg=c.TEXT_DARK,
        font=(c.FONT_FAMILY, 11, "bold"),
        anchor="w",
    ).pack(
        fill="x",
        pady=(0, 7),
    )

    pilih_prodi = ttk.Combobox(
        kolom_kanan,
        state="disabled",
        style="Form.TCombobox",
        width=30,
    )

    pilih_prodi.pack(
        fill="x",
        pady=(0, 18),
    )

    prodi_rows = []

    # ==============================================================
    # PESAN
    # ==============================================================

    kotak_pesan, tampil = _buat_pesan(
        kartu,
        c.CARD_BG,
        lebar=700,
    )

    kotak_pesan.pack(
        fill="x",
        pady=(18, 10),
    )

    # ==============================================================
    # NAVIGASI
    # ==============================================================

    # Penting:
    # Jangan memakai side="bottom" pada tombol.
    # Kita beri area navigasi sendiri setelah pesan sehingga
    # tombol selalu berada di dalam alur layout normal.

    tombol_nav = tk.Frame(
        kartu,
        bg=c.CARD_BG,
    )

    tombol_nav.pack(
        fill="x",
        pady=(4, 0),
    )

    ttk.Button(
        tombol_nav,
        text="Batal",
        style="Secondary.TButton",
        command=dialog.destroy,
    ).pack(
        side="left",
    )

    tombol_daftar = ttk.Button(
        tombol_nav,
        text="Daftar Sekarang  →",
        style="Primary.TButton",
    )

    tombol_daftar.pack(
        side="right",
    )

    # ==============================================================
    # LOGIKA JURUSAN → PROGRAM STUDI
    # ==============================================================

    def muat_prodi(event=None):
        nonlocal prodi_rows

        prodi_rows = []

        pilih_prodi.set("")

        indeks = pilih_jurusan.current()

        if indeks < 0:
            pilih_prodi.configure(
                state="disabled",
            )
            pilih_prodi["values"] = ()
            return

        try:
            prodi_rows = auth.daftar_prodi(
                jurusan[indeks]["jurusan_id"],
            )

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database tidak tersedia",
                PESAN_DB.format(err=err),
                parent=dialog,
            )
            return

        pilih_prodi["values"] = [
            f"{p['nama_prodi']} ({p['jenjang']})"
            for p in prodi_rows
        ]

        pilih_prodi.configure(
            state=(
                "readonly"
                if prodi_rows
                else "disabled"
            ),
        )

        if not prodi_rows:
            tampil(
                "Jurusan ini belum memiliki program studi.",
                "info",
            )
        else:
            tampil("")

    pilih_jurusan.bind(
        "<<ComboboxSelected>>",
        muat_prodi,
    )

    # ==============================================================
    # PROSES PENDAFTARAN
    # ==============================================================

    def daftar(event=None):
        tampil("")

        nama = in_nama.get().strip()
        nim = in_nim.get().strip()

        # ----------------------------------------------------------
        # VALIDASI NAMA & NIM
        # ----------------------------------------------------------

        if not nama or not nim:
            tampil(
                "Nama dan NIM tidak boleh kosong.",
                "error",
            )

            if not nama:
                in_nama.focus_set()
            else:
                in_nim.focus_set()

            return

        if len(nim) != 9:
            tampil(
                "NIM harus berisi tepat 9 digit angka.",
                "error",
            )
            in_nim.focus_set()
            return

        # ----------------------------------------------------------
        # VALIDASI JURUSAN
        # ----------------------------------------------------------

        if pilih_jurusan.current() < 0:
            tampil(
                "Pilih jurusan terlebih dahulu.",
                "error",
            )
            pilih_jurusan.focus_set()
            return

        # ----------------------------------------------------------
        # VALIDASI PROGRAM STUDI
        # ----------------------------------------------------------

        if (
            pilih_prodi.current() < 0
            or not prodi_rows
        ):
            tampil(
                "Pilih program studi.",
                "error",
            )
            pilih_prodi.focus_set()
            return

        # ----------------------------------------------------------
        # SIMPAN
        # ----------------------------------------------------------

        try:
            nim_terdaftar = auth.registrasi_mahasiswa(
                nama,
                nim,
                prodi_rows[
                    pilih_prodi.current()
                ]["prodi_id"],
            )

        except AppError as err:
            tampil(
                str(err),
                "error",
            )
            return

        except mysql.connector.IntegrityError as err:

            if err.errno == 1062:
                tampil(
                    "NIM sudah terdaftar di sistem.",
                    "error",
                )
                in_nim.focus_set()

            elif err.errno == 1048:
                tampil(
                    (
                        "Struktur database belum mendukung "
                        "pendaftaran mandiri. Jalankan "
                        "database/migrate_student_public_registration.sql."
                    ),
                    "error",
                )

            else:
                tampil(
                    f"Gagal menyimpan pendaftaran: {err}",
                    "error",
                )

            return

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database tidak tersedia",
                PESAN_DB.format(err=err),
                parent=dialog,
            )
            return

        # ----------------------------------------------------------
        # BERHASIL
        # ----------------------------------------------------------

        dialog.destroy()

        setelah_daftar(
            nim_terdaftar,
            nama,
        )

    tombol_daftar.configure(
        command=daftar,
    )

    # --------------------------------------------------------------
    # ENTER = DAFTAR
    # --------------------------------------------------------------

    dialog.bind(
        "<Return>",
        daftar,
    )

    # --------------------------------------------------------------
    # FOKUS AWAL
    # --------------------------------------------------------------

    in_nama.focus_set()
