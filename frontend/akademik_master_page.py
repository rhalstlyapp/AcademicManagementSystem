"""Ringkasan master akademik yang membaca backend jurusan hingga referensi nilai."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets import colors as c
from backend import jurusan, mata_kuliah, prodi, semester, skala_nilai


def _tab(notebook, title, rows, fields):
    frame = ttk.Frame(notebook, padding=12)
    notebook.add(frame, text=title)
    cols = [key for key, _label, _width in fields]
    table = ttk.Treeview(frame, columns=cols, show="headings")
    for key, label, width in fields:
        table.heading(key, text=label)
        table.column(key, width=width, anchor="w", stretch=True)
    table.tag_configure("genap", background="#F6F1EA")
    for index, row in enumerate(rows):
        table.insert(
            "", "end", values=tuple(row.get(key, "") for key in cols),
            tags=("genap" if index % 2 else "ganjil",),
        )

    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
    table.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    table.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    ttk.Label(
        frame, text=f"{len(rows)} data", foreground=c.TEXT_MUTED,
    ).grid(row=2, column=0, sticky="w", pady=(8, 0))


def tampilkan_master(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    header = tk.Frame(parent, bg=c.BG_COLOR)
    header.pack(fill="x", pady=(0, 16))
    tk.Label(
        header, text="Master Akademik", font=c.FONT_TITLE,
        bg=c.BG_COLOR, fg=c.TEXT_DARK,
    ).pack(anchor="w")
    tk.Label(
        header, text="Referensi jurusan, program studi, semester, dan penilaian.",
        font=c.FONT_BODY, bg=c.BG_COLOR, fg=c.TEXT_MUTED,
    ).pack(anchor="w", pady=(4, 0))
    try:
        daftar_jurusan = jurusan.daftar_jurusan()
        program_studi = prodi.daftar_prodi()
        daftar_semester = semester.daftar()
        daftar_mk = mata_kuliah.daftar()
        skala = skala_nilai.daftar()
    except mysql.connector.Error as err:
        messagebox.showerror("Database", str(err), parent=parent)
        return

    tabs = ttk.Notebook(parent)
    tabs.pack(fill="both", expand=True)
    _tab(tabs, "Jurusan", daftar_jurusan, (
        ("kode_jurusan", "Kode", 110),
        ("nama_jurusan", "Nama Jurusan", 280),
    ))
    _tab(tabs, "Program Studi", program_studi, (
        ("kode_prodi", "Kode", 90),
        ("nama_prodi", "Program Studi", 210),
        ("jenjang", "Jenjang", 80),
        ("nama_jurusan", "Jurusan", 220),
    ))
    _tab(tabs, "Semester", daftar_semester, (
        ("kode_semester", "Kode", 90),
        ("tahun_akademik", "Tahun Akademik", 130),
        ("jenis", "Jenis", 90),
        ("is_aktif", "Aktif", 70),
    ))
    _tab(tabs, "Mata Kuliah", daftar_mk, (
        ("kode_mk", "Kode", 100),
        ("nama_mk", "Nama Mata Kuliah", 230),
        ("sks", "SKS", 60),
        ("semester_paket", "Semester", 80),
        ("nama_prodi", "Program Studi", 200),
    ))
    _tab(tabs, "Skala Nilai", skala, (
        ("huruf_mutu", "Huruf", 70),
        ("bobot_mutu", "Bobot", 80),
        ("nilai_min", "Nilai Min", 90),
        ("nilai_max", "Nilai Maks", 90),
        ("is_lulus", "Lulus", 70),
    ))
