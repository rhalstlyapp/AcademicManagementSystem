"""Navigasi utama dan penghubung halaman setelah autentikasi."""
import tkinter as tk
from tkinter import messagebox

import mysql.connector

from assets.colors import BG_COLOR, CARD_BG, PRIMARY_COLOR, TEXT_DARK
from backend import auth, dashboard
from utils.validators import AppError


def tampilkan_dashboard(root, user):
    shell = tk.Frame(root, bg=BG_COLOR)
    shell.pack(fill="both", expand=True)

    header = tk.Frame(shell, bg=PRIMARY_COLOR, padx=20, pady=13)
    header.pack(fill="x")
    tk.Label(
        header,
        text=f"SIAKAD  |  {user['nama']} ({user['role'].title()})",
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Segoe UI", 12, "bold"),
    ).pack(side="left")

    def keluar():
        if messagebox.askyesno("Keluar", "Yakin ingin logout?", parent=root):
            auth.logout()
            shell.destroy()
            from frontend.login_page import tampilkan_login

            tampilkan_login(root)

    tk.Button(
        header,
        text="Logout",
        command=keluar,
        bg="white",
        fg=PRIMARY_COLOR,
        relief="flat",
        padx=12,
    ).pack(side="right")

    body = tk.Frame(shell, bg=BG_COLOR)
    body.pack(fill="both", expand=True)
    nav = tk.Frame(body, bg=CARD_BG, width=200, padx=12, pady=14)
    nav.pack(side="left", fill="y")
    nav.pack_propagate(False)
    content = tk.Frame(body, bg=BG_COLOR, padx=22, pady=20)
    content.pack(side="left", fill="both", expand=True)

    def bersihkan():
        for widget in content.winfo_children():
            widget.destroy()

    def halaman_awal():
        bersihkan()
        tk.Label(
            content,
            text=f"Selamat datang, {user['nama']}!",
            bg=BG_COLOR,
            fg=TEXT_DARK,
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            content,
            text="Pilih menu di sebelah kiri untuk membuka data akademik.",
            bg=BG_COLOR,
            fg=TEXT_DARK,
        ).pack(anchor="w", pady=(8, 20))
        try:
            data = dashboard.ringkasan()
        except (AppError, mysql.connector.Error) as err:
            tk.Label(content, text=f"Ringkasan database belum dapat dimuat: {err}", bg=BG_COLOR).pack(anchor="w")
            return
        kartu = tk.Frame(content, bg=BG_COLOR)
        kartu.pack(anchor="w", fill="x")
        for label, value in (
            ("Mahasiswa", data["jumlah_mahasiswa"]),
            ("Dosen aktif", data["jumlah_dosen_aktif"]),
            ("Program studi", data["jumlah_prodi"]),
            ("Semester aktif", data["semester_aktif"] or "Belum diatur"),
        ):
            box = tk.Frame(kartu, bg=CARD_BG, padx=18, pady=14)
            box.pack(side="left", padx=(0, 12), pady=(0, 12))
            tk.Label(box, text=label, bg=CARD_BG).pack(anchor="w")
            tk.Label(box, text=str(value), bg=CARD_BG, font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(4, 0))
        tk.Label(
            content,
            text=f"Login sebagai {user['role']} | Username: {user['username']}",
            bg=CARD_BG,
            padx=16,
            pady=14,
        ).pack(anchor="w")

    def buka_mahasiswa():
        from frontend.mahasiswa_page import tampilkan_mahasiswa

        tampilkan_mahasiswa(content)

    def buka_transkrip():
        from frontend.transkrip_page import tampilkan_transkrip

        tampilkan_transkrip(content, user)

    def buka_master():
        from frontend.akademik_master_page import tampilkan_master

        tampilkan_master(content)

    def buka_dosen():
        from frontend.dosen_page import tampilkan_dosen

        tampilkan_dosen(content)

    def buka_kelas():
        from frontend.kelas_page import tampilkan_kelas

        tampilkan_kelas(content)

    def buka_nilai():
        from frontend.nilai_page import tampilkan_nilai

        tampilkan_nilai(content, user)

    def buka_krs():
        from frontend.krs_page import tampilkan_krs

        tampilkan_krs(content, user)

    def tombol(label, command):
        tk.Button(
            nav,
            text=label,
            command=command,
            anchor="w",
            bg=CARD_BG,
            fg=TEXT_DARK,
            activebackground=BG_COLOR,
            relief="flat",
            padx=12,
            pady=10,
        ).pack(fill="x", pady=3)

    tombol("Beranda", halaman_awal)
    if user["role"] in ("admin", "dosen"):
        tombol("Data Mahasiswa", buka_mahasiswa)
        tombol("Nilai", buka_nilai)
    if user["role"] in ("dosen", "mahasiswa"):
        tombol("KRS", buka_krs)
    if user["role"] == "admin":
        tombol("Data Dosen", buka_dosen)
        tombol("Kelas Kuliah", buka_kelas)
        tombol("Master Akademik", buka_master)
    tombol("Transkrip & IPK", buka_transkrip)
    halaman_awal()
    return shell
