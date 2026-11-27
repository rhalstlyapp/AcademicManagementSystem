"""Halaman IPS, IPK, dan transkrip mahasiswa."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, TEXT_DARK
from backend import ipk, mahasiswa
from utils.validators import AppError


def tampilkan_transkrip(parent, user):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent,
        text="Transkrip & IPK",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 12))

    pilihan = None
    mahasiswa_id = user.get("mahasiswa_id")
    if user["role"] in ("admin", "dosen"):
        try:
            rows = mahasiswa.daftar()
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Data mahasiswa", str(err), parent=parent)
            return
        if not rows:
            tk.Label(parent, text="Belum ada data mahasiswa.", bg=BG_COLOR).pack(anchor="w")
            return
        pilihan = ttk.Combobox(
            parent,
            state="readonly",
            width=58,
            values=[f"{row['nim']} - {row['nama_lengkap']}" for row in rows],
        )
        pilihan.pack(anchor="w", pady=(0, 12))
        pilihan.current(0)
        ids = [row["mahasiswa_id"] for row in rows]

    ringkasan = tk.Frame(parent, bg=BG_COLOR)
    ringkasan.pack(fill="x", pady=(0, 14))
    columns = ("semester", "sks", "lulus", "ips")
    tabel_ips = ttk.Treeview(ringkasan, columns=columns, show="headings", height=5)
    for col, label, width in (
        ("semester", "Semester", 150),
        ("sks", "SKS Diambil", 110),
        ("lulus", "SKS Lulus", 100),
        ("ips", "IPS", 90),
    ):
        tabel_ips.heading(col, text=label)
        tabel_ips.column(col, width=width, anchor="center")
    tabel_ips.pack(side="left", fill="x", expand=True)

    nilai_ipk = tk.Label(
        ringkasan,
        text="IPK\n-",
        font=("Segoe UI", 17, "bold"),
        bg="#EFE8DD",
        padx=24,
        pady=18,
    )
    nilai_ipk.pack(side="left", padx=(14, 0), fill="y")

    tk.Label(
        parent,
        text="Daftar Nilai",
        font=("Segoe UI", 14, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 8))
    cols = ("semester", "kode", "mata_kuliah", "sks", "angka", "huruf", "status")
    tabel_nilai = ttk.Treeview(parent, columns=cols, show="headings", height=13)
    headings = {
        "semester": ("Semester", 100),
        "kode": ("Kode", 95),
        "mata_kuliah": ("Mata Kuliah", 240),
        "sks": ("SKS", 55),
        "angka": ("Nilai", 75),
        "huruf": ("Huruf", 65),
        "status": ("Status", 120),
    }
    for col in cols:
        title, width = headings[col]
        tabel_nilai.heading(col, text=title)
        tabel_nilai.column(col, width=width, anchor="w")
    tabel_nilai.pack(fill="both", expand=True)

    def muat(event=None):
        selected_id = mahasiswa_id
        if pilihan is not None:
            selected_id = ids[pilihan.current()]
        for table in (tabel_ips, tabel_nilai):
            for item in table.get_children():
                table.delete(item)
        try:
            data = ipk.ringkasan(selected_id)
        except AppError as err:
            messagebox.showerror("Transkrip", str(err), parent=parent)
            return
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database",
                f"Gagal memuat transkrip. Pastikan database/triggers_views.sql sudah dijalankan.\n\n{err}",
                parent=parent,
            )
            return

        stat = data["ipk"]
        nilai_ipk.config(text=f"IPK\n{stat['ipk'] if stat else '-'}")
        for item in data["ips"]:
            tabel_ips.insert(
                "",
                "end",
                values=(item["kode_semester"], item["sks_diambil"], item["sks_lulus"], item["ips"]),
            )
        for item in data["transkrip"]:
            tabel_nilai.insert(
                "",
                "end",
                values=(
                    item["kode_semester"],
                    item["kode_mk"],
                    item["nama_mk"],
                    item["sks"],
                    item["nilai_akhir"],
                    item["huruf_mutu"],
                    item["status_kelulusan"],
                ),
            )

    ttk.Button(parent, text="Muat Transkrip", command=muat).pack(anchor="w", pady=(8, 0))
    if pilihan is not None:
        pilihan.bind("<<ComboboxSelected>>", muat)
    muat()
