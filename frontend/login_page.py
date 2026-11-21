"""Halaman login Tkinter yang memanggil backend autentikasi."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, CARD_BG, PRIMARY_COLOR, TEXT_DARK
from backend import auth
from utils.validators import AppError


def tampilkan_login(root):
    frame = tk.Frame(root, bg=BG_COLOR)
    frame.pack(fill="both", expand=True)

    kartu = tk.Frame(frame, bg=CARD_BG, padx=38, pady=32)
    kartu.place(relx=0.5, rely=0.46, anchor="center")

    tk.Label(
        kartu,
        text="SIAKAD",
        font=("Segoe UI", 26, "bold"),
        bg=CARD_BG,
        fg=PRIMARY_COLOR,
    ).pack(anchor="w")
    tk.Label(
        kartu,
        text="Masuk menggunakan username admin atau NIM mahasiswa/dosen.",
        bg=CARD_BG,
        fg=TEXT_DARK,
        wraplength=360,
        justify="left",
    ).pack(anchor="w", pady=(4, 22))

    tk.Label(kartu, text="Username / NIM", bg=CARD_BG).pack(anchor="w")
    username = ttk.Entry(kartu, width=42)
    username.pack(fill="x", pady=(4, 14))

    tk.Label(kartu, text="Password", bg=CARD_BG).pack(anchor="w")
    password = ttk.Entry(kartu, width=42, show="•")
    password.pack(fill="x", pady=(4, 18))

    def masuk(event=None):
        try:
            user = auth.login(username.get(), password.get())
        except AppError as err:
            messagebox.showerror("Login gagal", str(err), parent=root)
            password.focus_set()
            return
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database tidak tersedia",
                f"Tidak dapat mengakses database. Periksa konfigurasi .env dan server MySQL.\n\n{err}",
                parent=root,
            )
            return
        root.unbind("<Return>")
        frame.destroy()
        from frontend.dashboard_page import tampilkan_dashboard

        tampilkan_dashboard(root, user)

    ttk.Button(kartu, text="Masuk", command=masuk).pack(fill="x")
    tk.Label(
        kartu,
        text="Akun mahasiswa dibuat oleh administrator.",
        bg=CARD_BG,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(16, 0))

    root.bind("<Return>", masuk)
    username.focus_set()
    return frame
