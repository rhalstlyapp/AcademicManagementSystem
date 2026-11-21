"""Ringkasan master akademik yang membaca backend jurusan hingga referensi nilai."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, TEXT_DARK
from backend import jurusan, mata_kuliah, prodi, semester, skala_nilai


def _tab(notebook, title, rows, fields):
    frame = ttk.Frame(notebook, padding=8)
    notebook.add(frame, text=title)
    cols = [key for key, _label, _width in fields]
    table = ttk.Treeview(frame, columns=cols, show="headings")
    for key, label, width in fields:
        table.heading(key, text=label)
        table.column(key, width=width, anchor="w")
    for row in rows:
        table.insert("", "end", values=tuple(row.get(key, "") for key in cols))
    table.pack(fill="both", expand=True)


def tampilkan_master(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    tk.Label(
        parent,
        text="Master Akademik",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 12))
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
