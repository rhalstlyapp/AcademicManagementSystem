"""Kalender dan daftar tugas pribadi untuk mahasiswa."""
import calendar
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import mysql.connector

from assets import colors as c
from backend import tugas
from utils.validators import AppError

NAMA_BULAN = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)
NAMA_HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")


def tampilkan_tugas(parent, user):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent, text="Agenda Tugas", font=c.FONT_TITLE,
        bg=c.BG_COLOR, fg=c.TEXT_DARK,
    ).pack(anchor="w", pady=(0, 4))
    tk.Label(
        parent, text="Catat tugas berdasarkan tanggal dan tandai saat sudah selesai.",
        font=c.FONT_BODY, bg=c.BG_COLOR, fg=c.TEXT_MUTED,
    ).pack(anchor="w", pady=(0, 18))

    area = tk.Frame(parent, bg=c.BG_COLOR)
    area.pack(fill="both", expand=True)
    kalender = tk.Frame(
        area, bg=c.CARD_BG, padx=16, pady=16, width=330,
        highlightthickness=1, highlightbackground=c.BORDER_COLOR,
    )
    kalender.pack(side="left", fill="y", padx=(0, 14))
    kalender.pack_propagate(False)
    agenda = tk.Frame(
        area, bg=c.CARD_BG, padx=20, pady=18,
        highlightthickness=1, highlightbackground=c.BORDER_COLOR,
    )
    agenda.pack(side="left", fill="both", expand=True)

    keadaan = {"tanggal": date.today(), "ringkasan": {}}
    label_bulan = tk.Label(
        kalender, text="", font=c.FONT_HEADING,
        bg=c.CARD_BG, fg=c.TEXT_DARK,
    )
    label_bulan.pack(pady=(0, 12))
    navigasi = tk.Frame(kalender, bg=c.CARD_BG)
    navigasi.pack(fill="x", pady=(0, 8))
    tombol_bulan = tk.Frame(navigasi, bg=c.CARD_BG)
    tombol_bulan.pack(side="left")
    ttk.Button(
        tombol_bulan, text="‹", width=3, style="Secondary.TButton",
        command=lambda: geser_bulan(-1),
    ).pack(side="left", padx=(0, 4))
    ttk.Button(
        tombol_bulan, text="›", width=3, style="Secondary.TButton",
        command=lambda: geser_bulan(1),
    ).pack(side="left")
    ttk.Button(
        navigasi, text="Hari ini", style="Secondary.TButton",
        command=lambda: pilih_tanggal(date.today()),
    ).pack(side="right")

    kisi = tk.Frame(kalender, bg=c.CARD_BG)
    kisi.pack(fill="x")
    for kolom, nama in enumerate(("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")):
        kisi.columnconfigure(kolom, weight=1)
        tk.Label(
            kisi, text=nama, bg=c.CARD_BG, fg=c.TEXT_MUTED,
            font=c.FONT_SMALL, width=4,
        ).grid(row=0, column=kolom, pady=(0, 4))

    tanggal_terpilih = tk.Label(
        agenda, text="", bg=c.CARD_BG, fg=c.TEXT_DARK,
        font=c.FONT_HEADING,
    )
    tanggal_terpilih.pack(anchor="w")
    ringkasan_hari = tk.Label(
        agenda, text="", bg=c.CARD_BG, fg=c.TEXT_MUTED,
        font=c.FONT_SMALL,
    )
    ringkasan_hari.pack(anchor="w", pady=(4, 12))
    ttk.Button(
        agenda, text="+ Tambah tugas", style="Primary.TButton",
        command=lambda: buka_form_tugas(),
    ).pack(anchor="w", pady=(0, 14))
    daftar = tk.Frame(agenda, bg=c.CARD_BG)
    daftar.pack(fill="both", expand=True)
    status = tk.Label(
        daftar, text="", bg=c.CARD_BG, fg=c.TEXT_MUTED,
        font=c.FONT_BODY, wraplength=650, justify="left",
    )
    status.pack(anchor="w")
    area_daftar = tk.Frame(daftar, bg=c.CARD_BG)
    area_daftar.pack(fill="both", expand=True, pady=(8, 0))
    kanvas_tugas = tk.Canvas(
        area_daftar, bg=c.CARD_BG, highlightthickness=0,
    )
    gulir = ttk.Scrollbar(area_daftar, orient="vertical", command=kanvas_tugas.yview)
    kanvas_tugas.configure(yscrollcommand=gulir.set)
    kanvas_tugas.pack(side="left", fill="both", expand=True)
    gulir.pack(side="right", fill="y")
    baris_tugas = tk.Frame(kanvas_tugas, bg=c.CARD_BG)
    jendela_tugas = kanvas_tugas.create_window(
        (0, 0), window=baris_tugas, anchor="nw",
    )
    baris_tugas.bind(
        "<Configure>",
        lambda event: kanvas_tugas.configure(scrollregion=kanvas_tugas.bbox("all")),
    )
    kanvas_tugas.bind(
        "<Configure>",
        lambda event: kanvas_tugas.itemconfigure(jendela_tugas, width=event.width),
    )

    def pesan_error(err):
        if isinstance(err, mysql.connector.Error) and err.errno == 1146:
            return (
                "Tabel agenda belum tersedia. Jalankan "
                "database/create_tugas_mahasiswa.sql pada database siakad."
            )
        return str(err)

    def gambar_kalender():
        for widget in kisi.grid_slaves():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()
        tanggal = keadaan["tanggal"]
        label_bulan.configure(text=f"{NAMA_BULAN[tanggal.month - 1]} {tanggal.year}")
        try:
            rows = tugas.daftar_bulan(tanggal.year, tanggal.month)
            keadaan["ringkasan"] = {row["tanggal"].day: row for row in rows}
        except (AppError, mysql.connector.Error) as err:
            keadaan["ringkasan"] = {}
            status.configure(text=pesan_error(err), fg=c.DANGER_COLOR)
        else:
            status.configure(text="", fg=c.TEXT_MUTED)

        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(
            tanggal.year, tanggal.month,
        )
        for indeks_minggu, minggu in enumerate(weeks, start=1):
            for kolom, hari in enumerate(minggu):
                if hari == 0:
                    continue
                punya_tugas = hari in keadaan["ringkasan"]
                aktif = date(tanggal.year, tanggal.month, hari) == keadaan["tanggal"]
                latar = c.PRIMARY_ACCENT if aktif else (
                    c.SURFACE_MUTED if punya_tugas else c.CARD_BG
                )
                warna = "#FFF8F0" if aktif else c.TEXT_DARK
                teks = f"{hari}\n•" if punya_tugas else str(hari)
                tombol = tk.Button(
                    kisi, text=teks, width=4, height=2,
                    font=c.FONT_SMALL, relief="flat", bd=0,
                    bg=latar, fg=warna, activebackground=c.PRIMARY_ACCENT,
                    activeforeground="#FFF8F0", cursor="hand2",
                    command=lambda d=hari: pilih_tanggal(date(
                        keadaan["tanggal"].year, keadaan["tanggal"].month, d,
                    )),
                )
                tombol.grid(row=indeks_minggu, column=kolom, padx=2, pady=2)

    def gambar_daftar():
        for widget in baris_tugas.winfo_children():
            widget.destroy()
        tanggal = keadaan["tanggal"]
        tanggal_terpilih.configure(
            text=f"{NAMA_HARI[tanggal.weekday()]}, {tanggal.day} "
                 f"{NAMA_BULAN[tanggal.month - 1]} {tanggal.year}"
        )
        try:
            rows = tugas.daftar_tanggal(tanggal)
        except (AppError, mysql.connector.Error) as err:
            ringkasan_hari.configure(text="")
            status.configure(text=pesan_error(err), fg=c.DANGER_COLOR)
            return

        jumlah_selesai = sum(bool(row["selesai"]) for row in rows)
        ringkasan_hari.configure(
            text=f"{len(rows)} tugas · {jumlah_selesai} selesai"
        )
        status.configure(
            text="Belum ada tugas untuk tanggal ini." if not rows else "",
            fg=c.TEXT_MUTED,
        )
        for row in rows:
            selesai = bool(row["selesai"])
            kartu = tk.Frame(
                baris_tugas,
                bg=c.SURFACE_MUTED if selesai else c.CARD_BG,
                padx=10, pady=8,
                highlightthickness=1, highlightbackground=c.BORDER_COLOR,
            )
            kartu.pack(fill="x", pady=(0, 8))
            var_selesai = tk.BooleanVar(master=parent, value=selesai)
            ttk.Checkbutton(
                kartu, variable=var_selesai, style="Form.TCheckbutton",
                command=lambda task=row, var=var_selesai: ubah_status(task, var),
            ).pack(side="left", padx=(0, 8))
            teks_tugas = tk.Frame(
                kartu, bg=c.SURFACE_MUTED if selesai else c.CARD_BG,
            )
            teks_tugas.pack(side="left", fill="x", expand=True)
            tk.Label(
                teks_tugas, text=row["judul"],
                bg=c.SURFACE_MUTED if selesai else c.CARD_BG,
                fg=c.TEXT_MUTED if selesai else c.TEXT_DARK,
                font=(c.FONT_FAMILY, 10, "overstrike" if selesai else "bold"),
                anchor="w", justify="left", wraplength=560,
            ).pack(anchor="w", fill="x")
            if row.get("catatan"):
                tk.Label(
                    teks_tugas, text=row["catatan"],
                    bg=c.SURFACE_MUTED if selesai else c.CARD_BG,
                    fg=c.TEXT_MUTED, font=c.FONT_SMALL,
                    anchor="w", justify="left", wraplength=560,
                ).pack(anchor="w", fill="x", pady=(3, 0))
            ttk.Button(
                kartu, text="Hapus", style="Secondary.TButton",
                command=lambda task_id=row["tugas_id"]: hapus_tugas(task_id),
            ).pack(side="right", padx=(8, 0))

    def pilih_tanggal(tanggal):
        keadaan["tanggal"] = tanggal
        gambar_kalender()
        gambar_daftar()

    def geser_bulan(delta):
        tanggal = keadaan["tanggal"]
        nomor = tanggal.year * 12 + tanggal.month - 1 + delta
        tahun, bulan_nol = divmod(nomor, 12)
        bulan = bulan_nol + 1
        hari = min(tanggal.day, calendar.monthrange(tahun, bulan)[1])
        pilih_tanggal(date(tahun, bulan, hari))

    def ubah_status(row, variabel):
        try:
            tugas.ubah_selesai(row["tugas_id"], variabel.get())
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Agenda Tugas", pesan_error(err), parent=parent)
        gambar_kalender()
        gambar_daftar()

    def hapus_tugas(tugas_id):
        if not messagebox.askyesno(
            "Hapus tugas", "Hapus catatan tugas ini?", parent=parent,
        ):
            return
        try:
            tugas.hapus(tugas_id)
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Agenda Tugas", pesan_error(err), parent=parent)
            return
        gambar_kalender()
        gambar_daftar()

    def buka_form_tugas():
        dialog = tk.Toplevel(parent.winfo_toplevel())
        dialog.title("Tambah Tugas")
        dialog.configure(bg=c.BG_COLOR)
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        form = tk.Frame(
            dialog, bg=c.CARD_BG, padx=24, pady=22,
            highlightthickness=1, highlightbackground=c.BORDER_COLOR,
        )
        form.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(form, text="Tugas apa yang perlu dikerjakan?",
                 bg=c.CARD_BG, fg=c.TEXT_DARK, font=c.FONT_HEADING).pack(anchor="w")
        tk.Label(form, text="Judul tugas", bg=c.CARD_BG, fg=c.TEXT_DARK,
                 font=c.FONT_BOLD).pack(anchor="w", pady=(16, 4))
        input_judul = ttk.Entry(form, style="Form.TEntry")
        input_judul.pack(fill="x")
        tk.Label(form, text="Tanggal (DD-MM-YYYY)", bg=c.CARD_BG,
                 fg=c.TEXT_DARK, font=c.FONT_BOLD).pack(anchor="w", pady=(12, 4))
        input_tanggal = ttk.Entry(form, style="Form.TEntry")
        input_tanggal.pack(fill="x")
        input_tanggal.insert(0, keadaan["tanggal"].strftime("%d-%m-%Y"))
        tk.Label(form, text="Catatan (opsional)", bg=c.CARD_BG,
                 fg=c.TEXT_DARK, font=c.FONT_BOLD).pack(anchor="w", pady=(12, 4))
        input_catatan = ttk.Entry(form, style="Form.TEntry")
        input_catatan.pack(fill="x")
        tombol = tk.Frame(form, bg=c.CARD_BG)
        tombol.pack(fill="x", side="bottom", pady=(18, 0))

        def simpan_tugas():
            try:
                tanggal = datetime.strptime(
                    input_tanggal.get().strip(), "%d-%m-%Y",
                ).date()
            except ValueError:
                messagebox.showerror(
                    "Tanggal tugas", "Masukkan tanggal dengan format DD-MM-YYYY.",
                    parent=dialog,
                )
                input_tanggal.focus_set()
                return
            try:
                tugas.tambah(input_judul.get(), tanggal, input_catatan.get())
            except (AppError, mysql.connector.Error) as err:
                messagebox.showerror("Agenda Tugas", pesan_error(err), parent=dialog)
                return
            dialog.destroy()
            pilih_tanggal(tanggal)

        ttk.Button(
            tombol, text="Batal", style="Secondary.TButton",
            command=dialog.destroy,
        ).pack(side="left")
        ttk.Button(
            tombol, text="Simpan tugas", style="Primary.TButton",
            command=simpan_tugas,
        ).pack(side="right")
        input_judul.focus_set()
        dialog.bind("<Return>", lambda event: simpan_tugas())
        dialog.bind("<Escape>", lambda event: dialog.destroy())

    gambar_kalender()
    gambar_daftar()
