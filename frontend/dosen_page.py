"""Halaman admin untuk membuat akun dan mengelola status dosen."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

<<<<<<< HEAD
from assets.colors import BG_COLOR, TEXT_DARK, TEXT_MUTED
=======
from assets.colors import BG_COLOR, TEXT_DARK
>>>>>>> 8c61a35 (feat: tambah pengelolaan dosen dan kelas)
from backend import dosen, prodi
from utils.validators import AppError


def tampilkan_dosen(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent,
        text="Data Dosen",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 12))

    bar = tk.Frame(parent, bg=BG_COLOR)
    bar.pack(fill="x", pady=(0, 10))
    cari = ttk.Entry(bar, width=32)
    cari.pack(side="left", padx=(0, 8))
    status = ttk.Combobox(
        bar,
        width=12,
        state="readonly",
        values=("Semua", "Aktif", "Cuti", "Pensiun", "Keluar"),
    )
    status.current(0)
    status.pack(side="left", padx=(0, 8))

    columns = ("nidn", "nip", "nama", "username", "prodi", "status")
    table = ttk.Treeview(parent, columns=columns, show="headings", height=18)
    for key, label, width in (
        ("nidn", "NIDN", 105),
        ("nip", "NIP", 140),
        ("nama", "Nama Dosen", 210),
        ("username", "Username", 130),
        ("prodi", "Program Studi", 220),
        ("status", "Status", 90),
    ):
        table.heading(key, text=label)
        table.column(key, width=width, anchor="w")
    table.pack(fill="both", expand=True)
<<<<<<< HEAD
    info_kosong = tk.Label(
        parent,
        text="Belum ada data dosen. Klik Tambah Dosen untuk membuat profil dan akun login.",
        font=("Segoe UI", 10),
        bg=BG_COLOR,
        fg=TEXT_MUTED,
        anchor="w",
    )

    def muat_data():
        info_kosong.pack_forget()
=======

    def muat_data():
>>>>>>> 8c61a35 (feat: tambah pengelolaan dosen dan kelas)
        for item in table.get_children():
            table.delete(item)
        try:
            rows = dosen.daftar(cari.get(), status.get() if status.get() != "Semua" else None)
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Data dosen", str(err), parent=parent)
            return
<<<<<<< HEAD
        if not rows:
            info_kosong.pack(fill="x", before=table, pady=(8, 4))
=======
>>>>>>> 8c61a35 (feat: tambah pengelolaan dosen dan kelas)
        for row in rows:
            table.insert(
                "",
                "end",
                iid=str(row["dosen_id"]),
                values=(
                    row["nidn"] or "",
                    row["nip"] or "",
                    row["nama_lengkap"],
                    row["username"],
                    f"{row['kode_prodi']} - {row['nama_prodi']}",
                    row["status"],
                ),
            )

    def tambah_dosen():
        try:
            prodi_rows = prodi.daftar_prodi()
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Program studi", str(err), parent=parent)
            return
        if not prodi_rows:
            messagebox.showwarning("Akun dosen", "Buat jurusan dan program studi terlebih dahulu.", parent=parent)
            return

<<<<<<< HEAD
        induk = parent.winfo_toplevel()
        dialog = tk.Toplevel(induk)
        dialog.title("Tambah Dosen")
        dialog.transient(induk)
        dialog.grab_set()
        dialog.geometry("900x620")
        dialog.minsize(780, 540)
        dialog.update_idletasks()
        x = induk.winfo_rootx() + max((induk.winfo_width() - 900) // 2, 0)
        y = induk.winfo_rooty() + max((induk.winfo_height() - 620) // 2, 0)
        dialog.geometry(f"900x620+{x}+{y}")
=======
        dialog = tk.Toplevel(parent.winfo_toplevel())
        dialog.title("Tambah Dosen")
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
>>>>>>> 8c61a35 (feat: tambah pengelolaan dosen dan kelas)
        form = ttk.Frame(dialog, padding=18)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        controls = {}
        row_index = 0

        def field(label, key, password=False):
            nonlocal row_index
            ttk.Label(form, text=label).grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=5)
            entry = ttk.Entry(form, width=36, show="*" if password else "")
            entry.grid(row=row_index, column=1, sticky="ew", pady=5)
            controls[key] = entry
            row_index += 1

        field("Username", "username")
        field("Email", "email")
        field("Password", "password", password=True)
        field("Nama lengkap", "nama")
        field("NIDN (boleh kosong)", "nidn")
        field("NIP (boleh kosong)", "nip")

        ttk.Label(form, text="Program studi").grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=5)
        pilihan_prodi = ttk.Combobox(
            form,
            state="readonly",
<<<<<<< HEAD
            width=76,
            height=14,
            values=[
                f"{row['nama_jurusan']} — {row['jenjang']} {row['nama_prodi']} ({row['kode_prodi']})"
                for row in prodi_rows
            ],
=======
            width=34,
            values=[f"{row['kode_prodi']} - {row['nama_prodi']} ({row['nama_jurusan']})" for row in prodi_rows],
>>>>>>> 8c61a35 (feat: tambah pengelolaan dosen dan kelas)
        )
        pilihan_prodi.grid(row=row_index, column=1, sticky="ew", pady=5)
        pilihan_prodi.current(0)
        row_index += 1

        ttk.Label(form, text="Jenis kelamin").grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=5)
        gender = ttk.Combobox(form, state="readonly", values=("L", "P"), width=34)
        gender.grid(row=row_index, column=1, sticky="ew", pady=5)
        row_index += 1

        def simpan():
            try:
                dosen.tambah(
                    username=controls["username"].get(),
                    email=controls["email"].get(),
                    password=controls["password"].get(),
                    nama=controls["nama"].get(),
                    prodi_id=prodi_rows[pilihan_prodi.current()]["prodi_id"],
                    jenis_kelamin=gender.get(),
                    nidn=controls["nidn"].get(),
                    nip=controls["nip"].get(),
                )
            except AppError as err:
                messagebox.showerror("Tambah dosen", str(err), parent=dialog)
                return
            except mysql.connector.Error as err:
                messagebox.showerror("Database", str(err), parent=dialog)
                return
            dialog.destroy()
            muat_data()

        ttk.Button(form, text="Simpan Dosen", command=simpan).grid(
            row=row_index, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )

    def ubah_status():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Status dosen", "Pilih dosen terlebih dahulu.", parent=parent)
            return
        dialog = tk.Toplevel(parent.winfo_toplevel())
        dialog.title("Ubah Status Dosen")
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        ttk.Label(dialog, text="Status baru", padding=(16, 14, 16, 4)).pack(anchor="w")
        choice = ttk.Combobox(dialog, state="readonly", values=("Aktif", "Cuti", "Pensiun", "Keluar"), width=24)
        choice.pack(fill="x", padx=16, pady=(0, 12))
        choice.set(table.set(selected[0], "status"))

        def simpan_status():
            try:
                dosen.ubah_status(int(selected[0]), choice.get())
            except (AppError, mysql.connector.Error) as err:
                messagebox.showerror("Ubah status", str(err), parent=dialog)
                return
            dialog.destroy()
            muat_data()

        ttk.Button(dialog, text="Simpan", command=simpan_status).pack(fill="x", padx=16, pady=(0, 16))

    ttk.Button(bar, text="Cari", command=muat_data).pack(side="left")
    ttk.Button(bar, text="Tambah Dosen", command=tambah_dosen).pack(side="right")
    ttk.Button(bar, text="Ubah Status", command=ubah_status).pack(side="right", padx=(0, 8))
    muat_data()
