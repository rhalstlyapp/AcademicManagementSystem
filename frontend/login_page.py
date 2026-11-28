"""Halaman login dan dialog pendaftaran mahasiswa (Tkinter + ttk) - Responsive Version."""

import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

# Pastikan modul ini ada di struktur project Anda
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
# PEMBANTU UTILITAS
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


def _buat_pesan(parent, latar, lebar_min=340):
    """Banner pesan dengan ikon & warna status. Disembunyikan saat kosong."""
    luar = tk.Frame(parent, bg=latar)
    # Gunakan pack_propagate False jika ingin tinggi tetap, tapi biarkan dinamis untuk fleksibilitas
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
        wraplength=lebar_min,  # Wrap text agar tidak melebar tak terkendali
        justify="left",
        anchor="w",
        padx=6,
        pady=10, # Tambah padding vertikal agar tidak dempet
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

        kotak.pack(fill="x", expand=True)

    return luar, tampil


def _kolom(parent, latar, teks, show=None, lebar=38, nim=False):
    """Label + entry dengan spacing yang lebih lega."""
    bungkus = tk.Frame(parent, bg=latar)
    bungkus.pack(fill="x", pady=(0, 20)) # Jarak antar input ditambah

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

    entry.pack(fill="x", ipady=4) # ipady membuat area ketik lebih tinggi

    return entry


def _kosongkan(entry, isi=""):
    entry.delete(0, "end")
    if isi:
        entry.insert(0, isi)


def _tengahkan(jendela, induk, lebar, tinggi):
    induk.update_idletasks()
    x = induk.winfo_rootx() + max((induk.winfo_width() - lebar) // 2, 0)
    y = induk.winfo_rooty() + max((induk.winfo_height() - tinggi) // 2, 0)
    
    # Pastikan tidak keluar layar
    screen_w = induk.winfo_screenwidth()
    screen_h = induk.winfo_screenheight()
    
    if x < 0: x = 0
    if y < 0: y = 0
    
    jendela.geometry(f"{lebar}x{tinggi}+{x}+{y}")


def _buat_kartu_ingat(parent, judul, keterangan):
    """Kartu pilihan ingat akun dengan area klik yang lebih besar."""
    pilihan = tk.BooleanVar(master=parent, value=True)

    kartu = tk.Frame(
        parent,
        bg=c.SURFACE_MUTED,
        padx=16,
        pady=14,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
        takefocus=True,
    )
    kartu.pack(fill="x", pady=(10, 20)) # Jarak bawah ditambah

    indikator = tk.Canvas(
        kartu,
        width=24,
        height=24,
        bg=c.SURFACE_MUTED,
        highlightthickness=0,
        cursor="hand2",
    )
    indikator.pack(side="left", padx=(0, 12))

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
    label_keterangan.pack(fill="x", pady=(4, 0))

    def gambar():
        aktif = pilihan.get()
        latar = _KARTU_INGAT_AKTIF if aktif else c.CARD_BG
        garis = c.PRIMARY_ACCENT if aktif else c.BORDER_COLOR

        kartu.configure(bg=latar, highlightbackground=garis)
        teks.configure(bg=latar)
        label_judul.configure(bg=latar)
        label_keterangan.configure(bg=latar)
        indikator.configure(bg=latar)

        indikator.delete("all")
        indikator.create_rectangle(
            2, 2, 22, 22,
            fill=c.PRIMARY_ACCENT if aktif else c.CARD_BG,
            outline=c.PRIMARY_ACCENT if aktif else c.BORDER_COLOR,
            width=2,
        )

        if aktif:
            indikator.create_line(
                6, 12, 10, 16, 18, 8,
                fill=_TEKS_TERANG, width=2, capstyle="round", joinstyle="round"
            )

    def toggle(event=None):
        pilihan.set(not pilihan.get())
        gambar()
        kartu.focus_set()
        return "break"

    for widget in (kartu, indikator, teks, label_judul, label_keterangan):
        widget.bind("<Button-1>", toggle)
        widget.bind("<space>", toggle)

    gambar()
    return pilihan


def _pasang_saran(root, entry, records, label_key, saat_dipilih):
    """Autocomplete popup."""
    popup = tk.Toplevel(root)
    popup.withdraw()
    popup.overrideredirect(True)
    popup.transient(root)

    daftar = tk.Listbox(
        popup,
        height=6, # Tinggi default sedikit ditambah
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
        try:
            x = root.winfo_pointerx()
            y = root.winfo_pointery()
            kiri = widget.winfo_rootx()
            atas = widget.winfo_rooty()
            return (kiri <= x < kiri + widget.winfo_width() and 
                    atas <= y < atas + widget.winfo_height())
        except tk.TclError:
            return False

    def pointer_di_area():
        return pointer_di(entry) or (popup.winfo_viewable() and pointer_di(daftar))

    def perbarui(event=None, semua=False):
        if not pointer_di_area():
            tutup()
            return

        teks = entry.get().strip().casefold()
        cocok[:] = [
            record for record in records
            if (semua or not teks or teks in str(record[label_key]).casefold())
        ]

        daftar.delete(0, "end")
        for record in cocok:
            daftar.insert("end", record[label_key])

        if not cocok:
            tutup()
            return

        daftar.configure(height=min(len(cocok), 6))
        root.update_idletasks()

        try:
            x = entry.winfo_rootx()
            y = entry.winfo_rooty() + entry.winfo_height()
            tinggi = daftar.winfo_reqheight() + 4
            
            # Cek batas layar bawah
            if y + tinggi > root.winfo_screenheight():
                y = entry.winfo_rooty() - tinggi

            popup.geometry(f"{entry.winfo_width()}x{tinggi}+{x}+{y}")
            popup.deiconify()
            popup.lift()
        except tk.TclError:
            pass

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

    def fokus_keluar(event=None):
        root.after(150, lambda: tutup() if root.focus_get() not in (entry, daftar) else None)

    def ketik(event=None):
        if event.keysym not in ("Up", "Down", "Return", "Escape", "Tab"):
            perbarui()

    # Binding events
    entry.bind("<Enter>", lambda e: perbarui(semua=True))
    entry.bind("<Leave>", lambda e: root.after(100, lambda: tutup() if not pointer_di_area() else None))
    entry.bind("<KeyRelease>", ketik)
    entry.bind("<Down>", panah_bawah)
    entry.bind("<Return>", enter)
    entry.bind("<Escape>", escape)
    entry.bind("<FocusOut>", fokus_keluar)

    daftar.bind("<ButtonRelease-1>", pilih)
    daftar.bind("<Motion>", sorot)
    daftar.bind("<Leave>", lambda e: (hilangkan_sorot(), root.after(100, lambda: tutup() if not pointer_di_area() else None)))
    daftar.bind("<Return>", pilih)
    daftar.bind("<Escape>", escape)
    daftar.bind("<FocusOut>", fokus_keluar)

    return perbarui, popup


# ======================================================================
# BRAND PANEL
# ======================================================================

def _panel_brand(frame):
    """Panel kiri: gradasi hijau kampus + aksen geometris akademik."""
    kiri = tk.Frame(frame, bg=c.PRIMARY_GRADIENT_BOT)
    kiri.grid(row=0, column=0, sticky="nsew")

    kanvas = tk.Canvas(kiri, highlightthickness=0, bd=0)
    kanvas.place(relwidth=1, relheight=1)

    r_top, g_top, b_top = _hex_ke_rgb(c.PRIMARY_GRADIENT_TOP)
    r_bot, g_bot, b_bot = _hex_ke_rgb(c.PRIMARY_GRADIENT_BOT)

    def _gambar_gradasi(event=None):
        kanvas.delete("grad")
        w = kanvas.winfo_width() or 1
        h = kanvas.winfo_height() or 1
        langkah = max(h // 40, 1)

        for i in range(0, h, langkah):
            rasio = i / h
            r = int(r_top + (r_bot - r_top) * rasio)
            g = int(g_top + (g_bot - g_top) * rasio)
            b = int(b_top + (b_bot - b_top) * rasio)
            kanvas.create_rectangle(0, i, w, i + langkah, fill=_rgb_ke_hex(r, g, b), outline="", tags="grad")

        # Dekorasi lingkaran
        kanvas.create_oval(-140, -140, 260, 260, fill=c.PRIMARY_HOVER, outline="", stipple="gray50", tags="grad")
        kanvas.create_oval(w - 180, h - 180, w + 100, h + 100, fill=c.PRIMARY_ACCENT, outline="", stipple="gray25", tags="grad")

    kanvas.bind("<Configure>", _gambar_gradasi)

    # Konten Brand menggunakan Frame transparan di atas canvas
    isi = tk.Frame(kanvas, bg=c.PRIMARY_GRADIENT_TOP) # Note: bg harus match top gradient untuk efek transparansi semu
    # Agar benar-benar transparan di Tkinter sulit, kita set bg sama dengan background canvas area tengah
    # Atau biarkan solid jika desain mengizinkan. Di sini kita gunakan solid color gradient top sebagai base frame isi.
    
    # Centering content
    isi.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8) 

    badge = tk.Frame(isi, bg=c.PRIMARY_ACCENT, padx=18, pady=10)
    badge.pack(anchor="w", pady=(0, 28))

    tk.Label(badge, text="🎓", font=(c.FONT_FAMILY, 18, "bold"), bg=c.PRIMARY_ACCENT, fg=_TEKS_TERANG).pack(side="left", padx=(0, 9))
    tk.Label(badge, text="SIAKAD", font=(c.FONT_FAMILY, 18, "bold"), bg=c.PRIMARY_ACCENT, fg=_TEKS_TERANG).pack(side="left")

    tk.Label(isi, text="Portal Akademik\nIPK & Penugasan", font=(c.FONT_FAMILY, 27, "bold"), bg=c.PRIMARY_GRADIENT_TOP, fg=_TEKS_TERANG, justify="left").pack(anchor="w")
    
    tk.Label(isi, text="Kelola tugas kuliah, rekap nilai,\ndan pantau IPS/IPK secara terstruktur.", 
             font=(c.FONT_FAMILY, 13), bg=c.PRIMARY_GRADIENT_TOP, fg=c.PRIMARY_LIGHT, justify="left").pack(anchor="w", pady=(12, 36))

    for baris in ("Monitoring tugas & tenggat kuliah", "Kalkulasi IPS & IPK akurat", "Akses terpisah Admin, Dosen & Mahasiswa"):
        baris_frame = tk.Frame(isi, bg=c.PRIMARY_GRADIENT_TOP)
        baris_frame.pack(anchor="w", pady=7)
        tk.Label(baris_frame, text="✓", font=(c.FONT_FAMILY, 13, "bold"), bg=c.PRIMARY_GRADIENT_TOP, fg=c.PRIMARY_LIGHT, width=2, anchor="w").pack(side="left")
        tk.Label(baris_frame, text=baris, font=(c.FONT_FAMILY, 12), bg=c.PRIMARY_GRADIENT_TOP, fg=_TEKS_TERANG, anchor="w").pack(side="left")

    tk.Label(kiri, text="© Sistem Akademik Kampus", font=(c.FONT_FAMILY, 10), bg=c.PRIMARY_GRADIENT_BOT, fg=_FOOTER_MUTED).place(relx=0.5, rely=0.96, anchor="center")


# ======================================================================
# LOGIN
# ======================================================================

def tampilkan_login(root, setelah_login, pesan_awal=None):
    """Membangun layar login di dalam root dan mengembalikan frame-nya."""
    terapkan_style(root)
    
    # Set minimum size agar layout tidak hancur di layar kecil
    root.minsize(1024, 650)

    frame = tk.Frame(root, bg=c.BG_COLOR)
    frame.pack(fill="both", expand=True)

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=4, uniform="panel") # Kiri sedikit lebih kecil proporsinya
    frame.columnconfigure(1, weight=6, uniform="panel") # Kanan lebih lebar

    _panel_brand(frame)

    kanan = tk.Frame(frame, bg=c.BG_COLOR)
    kanan.grid(row=0, column=1, sticky="nsew")

    # --------------------------------------------------------------
    # KARTU LOGIN (Centered & Responsive)
    # --------------------------------------------------------------
    
    # Container untuk men-center kartu
    container_kanan = tk.Frame(kanan, bg=c.BG_COLOR)
    container_kanan.pack(fill="both", expand=True)

    kartu = tk.Frame(
        container_kanan,
        bg=c.CARD_BG,
        padx=50, # Padding horizontal dikurangi sedikit agar muat di layar medium
        pady=40,
        highlightthickness=1,
        highlightbackground=c.BORDER_COLOR,
    )
    
    # Gunakan place dengan relative positioning agar selalu di tengah
    kartu.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, width=600)

    # --------------------------------------------------------------
    # HEADER
    # --------------------------------------------------------------
    tk.Label(kartu, text="Selamat datang", font=(c.FONT_FAMILY, 28, "bold"), bg=c.CARD_BG, fg=c.TEXT_DARK).pack(anchor="w")
    tk.Label(kartu, text="Masuk sesuai peran Anda untuk mengakses IPK dan penugasan.", 
             font=(c.FONT_FAMILY, 13), bg=c.CARD_BG, fg=c.TEXT_MUTED, wraplength=500, justify="left", anchor="w").pack(anchor="w", pady=(8, 25))

    # --------------------------------------------------------------
    # SEGMENTED CONTROL
    # --------------------------------------------------------------
    bar_tab = tk.Frame(kartu, bg=c.TAB_IDLE_BG, padx=4, pady=4)
    bar_tab.pack(fill="x", pady=(0, 25))

    bar_tab.columnconfigure(0, weight=1, uniform="tab")
    bar_tab.columnconfigure(1, weight=1, uniform="tab")
    bar_tab.columnconfigure(2, weight=1, uniform="tab")

    tombol_tab = {}
    for kolom, (kunci, teks) in enumerate((
        ("mahasiswa", "🎓  Mahasiswa"),
        ("dosen", "📘  Dosen"),
        ("admin", "🏛️  Admin"),
    )):
        tombol_tab[kunci] = tk.Button(
            bar_tab, text=teks, font=(c.FONT_FAMILY, 12, "bold"), relief="flat", bd=0, cursor="hand2", padx=10, pady=12,
            command=lambda k=kunci: pilih_tab(k)
        )
        tombol_tab[kunci].grid(row=0, column=kolom, sticky="ew")

    # --------------------------------------------------------------
    # AREA FORM
    # --------------------------------------------------------------
    area = tk.Frame(kartu, bg=c.CARD_BG)
    area.pack(fill="x", expand=True) # Expand agar mengambil sisa ruang sebelum footer/tombol

    # ==============================================================
    # FORM MAHASISWA
    # ==============================================================
    form_mhs = tk.Frame(area, bg=c.CARD_BG)

    tk.Label(form_mhs, text="Nama lengkap", bg=c.CARD_BG, fg=c.TEXT_DARK, font=(c.FONT_FAMILY, 11, "bold"), anchor="w").pack(fill="x", pady=(0, 6))
    in_nama = ttk.Entry(form_mhs, width=38, style="Form.TEntry")
    in_nama.pack(fill="x", pady=(0, 18), ipady=4)

    in_nim = _kolom(form_mhs, c.CARD_BG, "NIM (9 digit)", lebar=38, nim=True)

    var_ingat = _buat_kartu_ingat(form_mhs, "Ingat akun mahasiswa di perangkat ini", "Nama dan NIM disimpan lokal agar login berikutnya lebih cepat.")

    akun_terakhir = muat_akun()

    def pilih_akun_mahasiswa(akun):
        _kosongkan(in_nama, akun["nama"])
        _kosongkan(in_nim, akun["nim"])

    saran_mahasiswa, popup_mahasiswa = _pasang_saran(root, in_nama, akun_terakhir, "nama", pilih_akun_mahasiswa)

    def ingat_akun(nama, nim):
        if not var_ingat.get(): return
        if simpan_akun(nama, nim):
            akun_terakhir[:] = muat_akun()
            if popup_mahasiswa.winfo_viewable(): saran_mahasiswa()

    # ==============================================================
    # FORM ADMIN / DOSEN
    # ==============================================================
    form_admin = tk.Frame(area, bg=c.CARD_BG)

    in_user = _kolom(form_admin, c.CARD_BG, "Username", lebar=38)

    bungkus_password = tk.Frame(form_admin, bg=c.CARD_BG)
    bungkus_password.pack(fill="x", pady=(0, 18))

    tk.Label(bungkus_password, text="Password", bg=c.CARD_BG, fg=c.TEXT_DARK, font=(c.FONT_FAMILY, 11, "bold"), anchor="w").pack(fill="x", pady=(0, 6))

    var_tampil = tk.BooleanVar(value=False)
    in_pass = ttk.Entry(bungkus_password, width=38, style="Form.TEntry", show="\u2022")
    in_pass.pack(fill="x", ipady=4)

    # Tombol Tampilkan Password
    bar_tampil = tk.Frame(bungkus_password, bg=c.CARD_BG, cursor="hand2")
    bar_tampil.pack(anchor="w", pady=(8, 0))

    ikon_mata = tk.Canvas(bar_tampil, width=20, height=16, bg=c.CARD_BG, highlightthickness=0, cursor="hand2")
    ikon_mata.pack(side="left", padx=(0, 5))

    tombol_tampil = tk.Button(bar_tampil, text="Tampilkan password", font=(c.FONT_FAMILY, 10), bg=c.CARD_BG, fg=c.TEXT_MUTED, activebackground=c.CARD_BG, activeforeground=c.PRIMARY_ACCENT, relief="flat", bd=0, padx=0, pady=1, cursor="hand2")
    tombol_tampil.pack(side="left")

    petunjuk_password = tk.Label(bungkus_password, text="", bg=c.CARD_BG, fg=c.TEXT_MUTED, font=(c.FONT_FAMILY, 10), anchor="w", justify="left", wraplength=520)

    def bersihkan_petunjuk_password(event=None):
        petunjuk_password.pack_forget()

    def gambar_mata():
        warna = c.PRIMARY_ACCENT if var_tampil.get() else c.TEXT_MUTED
        ikon_mata.delete("all")
        ikon_mata.create_oval(1, 2, 19, 14, outline=warna, width=1.5)
        ikon_mata.create_oval(7, 4, 13, 12, fill=warna, outline=warna)

    def ganti_tampil():
        in_pass.configure(show="" if var_tampil.get() else "\u2022")
        tombol_tampil.configure(text="Sembunyikan password" if var_tampil.get() else "Tampilkan password", fg=c.PRIMARY_ACCENT if var_tampil.get() else c.TEXT_MUTED)
        gambar_mata()

    def toggle_tampil(event=None):
        var_tampil.set(not var_tampil.get())
        ganti_tampil()
        return "break"

    tombol_tampil.configure(command=toggle_tampil)
    bar_tampil.bind("<Button-1>", toggle_tampil)
    ikon_mata.bind("<Button-1>", toggle_tampil)
    
    # Hover effects
    def hover_enter(e): tombol_tampil.configure(fg=c.PRIMARY_ACCENT)
    def hover_leave(e): tombol_tampil.configure(fg=c.PRIMARY_ACCENT if var_tampil.get() else c.TEXT_MUTED)
    
    for w in [ikon_mata, tombol_tampil]:
        w.bind("<Enter>", hover_enter)
        w.bind("<Leave>", hover_leave)
        
    tombol_tampil.bind("<space>", toggle_tampil)
    tombol_tampil.bind("<Return>", toggle_tampil)
    gambar_mata()

    var_ingat_staff = _buat_kartu_ingat(form_admin, "Ingat akun di perangkat ini", "Username akan disimpan agar login berikutnya lebih mudah.")

    fungsi_akun_staff = {
        "admin": (muat_username_admin, muat_password_admin, simpan_username_admin, simpan_akun_admin),
        "dosen": (muat_username_dosen, muat_password_dosen, simpan_username_dosen, simpan_akun_dosen),
    }
    akun_staff_aktif = []
    fungsi_hapus_akun_staff = {"admin": hapus_akun_admin, "dosen": hapus_akun_dosen}

    def muat_rekomendasi_staff(role):
        muat_username, muat_password, _, _ = fungsi_akun_staff[role]
        return [{"username": u, "password": muat_password(u)} for u in muat_username()]

    def pilih_username_staff(akun):
        _kosongkan(in_user, akun["username"])
        pwd = akun.get("password", "")
        _kosongkan(in_pass, pwd)
        if pwd:
            petunjuk_password.pack_forget()
        else:
            petunjuk_password.configure(text="Password akun ini belum tersimpan. Masukkan password dan login sekali dengan opsi ingat akun aktif.")
            petunjuk_password.pack(anchor="w", pady=(6, 0))

    in_pass.bind("<KeyRelease>", bersihkan_petunjuk_password, add="+")
    saran_staff, popup_staff = _pasang_saran(root, in_user, akun_staff_aktif, "username", pilih_username_staff)

    def ingat_akun_staff(role, username, password):
        if var_ingat_staff.get():
            _, _, simpan_username, simpan_akun_s = fungsi_akun_staff[role]
            simpan_username(username)
            simpan_akun_s(username, password)
        else:
            fungsi_hapus_akun_staff[role](username)
        akun_staff_aktif[:] = muat_rekomendasi_staff(role)

    if popup_staff.winfo_viewable(): saran_staff()

    # --------------------------------------------------------------
    # PESAN ERROR/INFO
    # --------------------------------------------------------------
    kotak_pesan, tampil_pesan = _buat_pesan(kartu, c.CARD_BG)
    kotak_pesan.pack(fill="x", pady=(10, 5))

    # --------------------------------------------------------------
    # TOMBOL MASUK
    # --------------------------------------------------------------
    tombol_masuk = ttk.Button(kartu, text="Masuk  →", style="Primary.TButton")
    tombol_masuk.pack(fill="x", pady=(15, 0), ipady=5) # ipady memperbesar tombol

    # --------------------------------------------------------------
    # REGISTER LINK
    # --------------------------------------------------------------
    pemisah = tk.Frame(kartu, bg=c.CARD_BG)
    pemisah.pack(fill="x", pady=(25, 0))

    tk.Label(pemisah, text="Belum punya akun?", font=(c.FONT_FAMILY, 11), bg=c.CARD_BG, fg=c.TEXT_MUTED).pack(side="left")
    tombol_daftar = ttk.Button(pemisah, text="Daftar sebagai mahasiswa", style="Link.TButton")
    tombol_daftar.pack(side="left", padx=(8, 0))

    aktif = {"tab": "mahasiswa"}

    # --------------------------------------------------------------
    # LOGIKA TAB
    # --------------------------------------------------------------
    def pilih_tab(kunci, kosongkan_pesan=True):
        role_sebelumnya = aktif["tab"]
        aktif["tab"] = kunci

        popup_mahasiswa.withdraw()
        popup_staff.withdraw()

        # Reset field staff jika pindah dari/to staff
        if role_sebelumnya != kunci and (role_sebelumnya in ("admin", "dosen") or kunci in ("admin", "dosen")):
            _kosongkan(in_user)
            _kosongkan(in_pass)
            petunjuk_password.pack_forget()

        for k, tombol in tombol_tab.items():
            if k == kunci:
                tombol.configure(bg=c.TAB_ACTIVE_BG, fg=_TEKS_TERANG, activebackground=c.PRIMARY_ACCENT, activeforeground=_TEKS_TERANG)
            else:
                tombol.configure(bg=c.TAB_IDLE_BG, fg=c.TEXT_MUTED, activebackground=c.INPUT_BORDER, activeforeground=c.TEXT_DARK)

        form_mhs.pack_forget()
        form_admin.pack_forget()

        if kunci == "mahasiswa":
            form_mhs.pack(fill="x")
            in_nama.focus_set()
        else:
            form_admin.pack(fill="x")
            akun_staff_aktif[:] = muat_rekomendasi_staff(kunci)
            in_user.focus_set()

        if kunci == "mahasiswa":
            pemisah.pack(fill="x", pady=(25, 0))
        else:
            pemisah.pack_forget()

        if kosongkan_pesan:
            tampil_pesan("")

    # --------------------------------------------------------------
    # LOGIKA LOGIN
    # --------------------------------------------------------------
    def masuk(event=None):
        tampil_pesan("")
        try:
            if aktif["tab"] == "mahasiswa":
                pengguna = auth.login_mahasiswa(in_nama.get(), in_nim.get())
            elif aktif["tab"] == "dosen":
                pengguna = auth.login_dosen(in_user.get(), in_pass.get())
            else:
                pengguna = auth.login_admin(in_user.get(), in_pass.get())
        except AppError as err:
            tampil_pesan(str(err), "error")
            if aktif["tab"] in ("admin", "dosen"):
                _kosongkan(in_pass)
                in_pass.focus_set()
            else:
                in_nim.focus_set()
            return
        except mysql.connector.Error as err:
            messagebox.showerror("Database tidak tersedia", PESAN_DB.format(err=err), parent=root)
            return

        if aktif["tab"] == "mahasiswa":
            ingat_akun(in_nama.get(), in_nim.get())
        else:
            ingat_akun_staff(aktif["tab"], in_user.get(), in_pass.get())

        root.unbind("<Return>")
        setelah_login(pengguna)

    def setelah_daftar(nim, nama):
        pilih_tab("mahasiswa")
        ingat_akun(nama, nim)
        _kosongkan(in_nama, nama)
        _kosongkan(in_nim, nim)
        tampil_pesan("Pendaftaran berhasil! Klik Masuk, lalu lengkapi biodata & dosen PA melalui administrator.", "sukses")
        tombol_masuk.focus_set()

    tombol_masuk.configure(command=masuk)
    tombol_daftar.configure(command=lambda: tampilkan_registrasi(root, setelah_daftar))
    root.bind("<Return>", masuk)

    pilih_tab("mahasiswa")
    if pesan_awal:
        tampil_pesan(*pesan_awal)

    return frame


# ======================================================================
# PENDAFTARAN (SCROLLABLE & RESPONSIVE)
# ======================================================================

def tampilkan_registrasi(root, setelah_daftar):
    """Dialog pendaftaran mahasiswa baru dengan dukungan scroll."""
    terapkan_style(root)

    try:
        jurusan = auth.daftar_jurusan()
    except mysql.connector.Error as err:
        messagebox.showerror("Database tidak tersedia", PESAN_DB.format(err=err), parent=root)
        return

    if not jurusan:
        messagebox.showinfo("Pendaftaran", "Data jurusan belum tersedia. Hubungi administrator.", parent=root)
        return

    # --------------------------------------------------------------
    # DIALOG UTAMA
    # --------------------------------------------------------------
    dialog = tk.Toplevel(root)
    dialog.title("Pendaftaran Mahasiswa Baru")
    dialog.configure(bg=c.BG_COLOR)
    dialog.resizable(False, False) # Bisa diubah ke True jika ingin user resize manual
    dialog.transient(root)
    
    # Ukuran awal yang lebih aman
    lebar_dialog = 950
    tinggi_dialog = 750
    
    _tengahkan(dialog, root, lebar_dialog, tinggi_dialog)

    # --------------------------------------------------------------
    # CANVAS & SCROLLBAR (Untuk mencegah crop)
    # --------------------------------------------------------------
    main_canvas = tk.Canvas(dialog, bg=c.BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=main_canvas.yview)
    
    scrollable_frame = tk.Frame(main_canvas, bg=c.CARD_BG)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)
    
    # Binding mouse wheel untuk scroll
    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Layout Canvas & Scrollbar
    main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)

    # --------------------------------------------------------------
    # KONTEN DI DALAM SCROLLABLE FRAME
    # --------------------------------------------------------------
    kartu = scrollable_frame
    kartu.configure(padx=50, pady=40, highlightthickness=1, highlightbackground=c.BORDER_COLOR)

    # Header
    tk.Label(kartu, text="Pendaftaran Mahasiswa Baru", font=(c.FONT_FAMILY, 24, "bold"), bg=c.CARD_BG, fg=c.TEXT_DARK).pack(anchor="w")
    tk.Label(kartu, text="Lengkapi data identitas dan akademik Anda di bawah ini.", font=(c.FONT_FAMILY, 12), bg=c.CARD_BG, fg=c.TEXT_MUTED, justify="left").pack(anchor="w", pady=(6, 20))
    tk.Frame(kartu, bg=c.BORDER_COLOR, height=1).pack(fill="x", pady=(0, 25))

    # Container 2 Kolom
    wadah_kolom = tk.Frame(kartu, bg=c.CARD_BG)
    wadah_kolom.pack(fill="x")
    wadah_kolom.columnconfigure(0, weight=1, uniform="kolom")
    wadah_kolom.columnconfigure(1, weight=1, uniform="kolom")

    # KOLOM KIRI - IDENTITAS
    kolom_kiri = tk.Frame(wadah_kolom, bg=c.CARD_BG)
    kolom_kiri.grid(row=0, column=0, sticky="nsew", padx=(0, 30)) # Jarak antar kolom ditambah

    tk.Label(kolom_kiri, text="Data Identitas", font=(c.FONT_FAMILY, 13, "bold"), bg=c.CARD_BG, fg=c.PRIMARY_DARK).pack(anchor="w", pady=(0, 15))
    
    in_nama = _kolom(kolom_kiri, c.CARD_BG, "Nama Lengkap", lebar=30)
    in_nim = _kolom(kolom_kiri, c.CARD_BG, "NIM (9 digit angka)", lebar=30, nim=True)

    # Info Keamanan Box
    frame_hint = tk.Frame(kolom_kiri, bg=_KOTAK_INFO_BG, padx=16, pady=14, highlightthickness=1, highlightbackground=_KOTAK_INFO_BORDER)
    frame_hint.pack(fill="x", pady=(10, 0))
    tk.Label(frame_hint, text="ℹ️   Info Keamanan", font=(c.FONT_FAMILY, 10, "bold"), bg=_KOTAK_INFO_BG, fg=_KOTAK_INFO_FG, anchor="w").pack(fill="x")
    tk.Label(frame_hint, text="NIM berfungsi sebagai kredensial masuk mahasiswa. Simpan baik-baik data ini.", font=(c.FONT_FAMILY, 10), bg=_KOTAK_INFO_BG, fg=_KOTAK_INFO_FG, justify="left", anchor="w", wraplength=300).pack(fill="x", pady=(5, 0))

    # KOLOM KANAN - AKADEMIK
    kolom_kanan = tk.Frame(wadah_kolom, bg=c.CARD_BG)
    kolom_kanan.grid(row=0, column=1, sticky="nsew", padx=(30, 0))

    tk.Label(kolom_kanan, text="Data Akademik", font=(c.FONT_FAMILY, 13, "bold"), bg=c.CARD_BG, fg=c.PRIMARY_DARK).pack(anchor="w", pady=(0, 15))

    tk.Label(kolom_kanan, text="Jurusan", bg=c.CARD_BG, fg=c.TEXT_DARK, font=(c.FONT_FAMILY, 11, "bold"), anchor="w").pack(fill="x", pady=(0, 7))
    pilih_jurusan = ttk.Combobox(kolom_kanan, state="readonly", style="Form.TCombobox", width=30)
    pilih_jurusan["values"] = [f"{j['nama_jurusan']} ({j['kode_jurusan']})" for j in jurusan]
    pilih_jurusan.pack(fill="x", pady=(0, 20), ipady=4)

    tk.Label(kolom_kanan, text="Program Studi", bg=c.CARD_BG, fg=c.TEXT_DARK, font=(c.FONT_FAMILY, 11, "bold"), anchor="w").pack(fill="x", pady=(0, 7))
    pilih_prodi = ttk.Combobox(kolom_kanan, state="disabled", style="Form.TCombobox", width=30)
    pilih_prodi.pack(fill="x", pady=(0, 20), ipady=4)

    prodi_rows = []

    # Pesan Error Dialog
    kotak_pesan, tampil = _buat_pesan(kartu, c.CARD_BG, lebar_min=700)
    kotak_pesan.pack(fill="x", pady=(20, 15))

    # Navigasi Bawah
    tombol_nav = tk.Frame(kartu, bg=c.CARD_BG)
    tombol_nav.pack(fill="x", pady=(10, 0))

    ttk.Button(tombol_nav, text="Batal", style="Secondary.TButton", command=dialog.destroy).pack(side="left")
    tombol_daftar = ttk.Button(tombol_nav, text="Daftar Sekarang  →", style="Primary.TButton")
    tombol_daftar.pack(side="right")

    # Logika Jurusan -> Prodi
    def muat_prodi(event=None):
        nonlocal prodi_rows
        prodi_rows = []
        pilih_prodi.set("")
        indeks = pilih_jurusan.current()
        if indeks < 0:
            pilih_prodi.configure(state="disabled")
            pilih_prodi["values"] = ()
            return
        
        try:
            prodi_rows = auth.daftar_prodi(jurusan[indeks]["jurusan_id"])
        except mysql.connector.Error as err:
            messagebox.showerror("Database tidak tersedia", PESAN_DB.format(err=err), parent=dialog)
            return

        pilih_prodi["values"] = [f"{p['nama_prodi']} ({p['jenjang']})" for p in prodi_rows]
        pilih_prodi.configure(state="readonly" if prodi_rows else "disabled")
        
        if not prodi_rows:
            tampil("Jurusan ini belum memiliki program studi.", "info")
        else:
            tampil("")

    pilih_jurusan.bind("<<ComboboxSelected>>", muat_prodi)

    # Logika Daftar
    def daftar(event=None):
        tampil("")
        nama = in_nama.get().strip()
        nim = in_nim.get().strip()

        if not nama or not nim:
            tampil("Nama dan NIM tidak boleh kosong.", "error")
            if not nama: in_nama.focus_set()
            else: in_nim.focus_set()
            return

        if len(nim) != 9:
            tampil("NIM harus berisi tepat 9 digit angka.", "error")
            in_nim.focus_set()
            return

        if pilih_jurusan.current() < 0:
            tampil("Pilih jurusan terlebih dahulu.", "error")
            pilih_jurusan.focus_set()
            return

        if pilih_prodi.current() < 0 or not prodi_rows:
            tampil("Pilih program studi.", "error")
            pilih_prodi.focus_set()
            return

        try:
            nim_terdaftar = auth.registrasi_mahasiswa(nama, nim, prodi_rows[pilih_prodi.current()]["prodi_id"])
        except AppError as err:
            tampil(str(err), "error")
            return
        except mysql.connector.IntegrityError as err:
            if err.errno == 1062:
                tampil("NIM sudah terdaftar di sistem.", "error")
                in_nim.focus_set()
            elif err.errno == 1048:
                tampil("Struktur database belum mendukung pendaftaran mandiri. Jalankan migrate_student_public_registration.sql.", "error")
            else:
                tampil(f"Gagal menyimpan pendaftaran: {err}", "error")
            return
        except mysql.connector.Error as err:
            messagebox.showerror("Database tidak tersedia", PESAN_DB.format(err=err), parent=dialog)
            return

        dialog.destroy()
        setelah_daftar(nim_terdaftar, nama)

    tombol_daftar.configure(command=daftar)
    dialog.bind("<Return>", daftar)
    
    # Fokus awal
    in_nama.focus_set()