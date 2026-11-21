"""Halaman KRS mahasiswa dan persetujuan KRS dosen PA."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, TEXT_DARK
from backend import krs
from utils.validators import AppError


def tampilkan_krs(parent, user):
    for widget in parent.winfo_children():
        widget.destroy()
    tk.Label(
        parent,
        text="Kartu Rencana Studi (KRS)",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 12))
    if user["role"] == "mahasiswa":
        _halaman_mahasiswa(parent)
    elif user["role"] == "dosen":
        _halaman_dosen(parent)


def _halaman_mahasiswa(parent):
    status_label = tk.Label(parent, text="", bg=BG_COLOR, fg=TEXT_DARK, anchor="w")
    status_label.pack(fill="x", pady=(0, 10))

    section = tk.Frame(parent, bg=BG_COLOR)
    section.pack(fill="both", expand=True)
    left = tk.Frame(section, bg=BG_COLOR)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))
    right = tk.Frame(section, bg=BG_COLOR)
    right.pack(side="left", fill="both", expand=True, padx=(8, 0))

    tk.Label(left, text="Kelas tersedia", bg=BG_COLOR, font=("Segoe UI", 12, "bold")).pack(anchor="w")
    available_cols = ("kode", "mata_kuliah", "kelas", "sks", "kuota")
    available = ttk.Treeview(left, columns=available_cols, show="headings", height=13)
    for key, label, width in (
        ("kode", "Kode", 75),
        ("mata_kuliah", "Mata Kuliah", 185),
        ("kelas", "Kelas", 55),
        ("sks", "SKS", 45),
        ("kuota", "Sisa", 55),
    ):
        available.heading(key, text=label)
        available.column(key, width=width, anchor="w")
    available.pack(fill="both", expand=True, pady=(6, 8))

    tk.Label(right, text="Pilihan KRS", bg=BG_COLOR, font=("Segoe UI", 12, "bold")).pack(anchor="w")
    selected_cols = ("kode", "mata_kuliah", "kelas", "sks")
    selected = ttk.Treeview(right, columns=selected_cols, show="headings", height=13)
    for key, label, width in (
        ("kode", "Kode", 75),
        ("mata_kuliah", "Mata Kuliah", 185),
        ("kelas", "Kelas", 55),
        ("sks", "SKS", 45),
    ):
        selected.heading(key, text=label)
        selected.column(key, width=width, anchor="w")
    selected.pack(fill="both", expand=True, pady=(6, 8))

    available_rows = []
    summary = None
    window_open = False

    def muat():
        nonlocal available_rows, summary, window_open
        for table in (available, selected):
            for item in table.get_children():
                table.delete(item)
        available_rows = []
        window_open = True
        try:
            available_rows = krs.kelas_tersedia()
        except AppError as err:
            window_open = False
            try:
                summary = krs.ringkasan_saya()
            except (AppError, mysql.connector.Error) as summary_err:
                status_label.config(text=str(summary_err))
                return
            status_label.config(text=f"{summary['semester']['kode_semester']}: {err}")
        except mysql.connector.Error as err:
            status_label.config(text=f"Gagal memuat kelas tersedia: {err}")
            return
        else:
            try:
                summary = krs.ringkasan_saya()
            except (AppError, mysql.connector.Error) as err:
                status_label.config(text=str(err))
                return

        term = summary["semester"]
        current = summary["krs"]
        state = current["status"] if current else "Belum dibuat"
        status_label.config(
            text=f"Semester {term['kode_semester']} · Status KRS: {state}"
            + (f" · Catatan PA: {current['catatan_pa']}" if current and current["catatan_pa"] else "")
        )
        if current:
            for row in summary["detail"]:
                selected.insert(
                    "",
                    "end",
                    iid=str(row["krs_detail_id"]),
                    values=(row["kode_mk"], row["nama_mk"], row["nama_kelas"], row["sks"]),
                )
        for row in available_rows:
            sisa = max(0, row["kuota"] - row["terdaftar"])
            available.insert(
                "",
                "end",
                iid=str(row["kelas_id"]),
                values=(row["kode_mk"], row["nama_mk"], row["nama_kelas"], row["sks"], sisa),
            )
        boleh_ubah = window_open and (current is None or current["status"] == "Draft")
        add_button.config(state="normal" if boleh_ubah else "disabled")
        remove_button.config(state="normal" if boleh_ubah else "disabled")
        submit_button.config(state="normal" if boleh_ubah and current else "disabled")

    def ambil():
        picked = available.selection()
        if not picked:
            messagebox.showwarning("KRS", "Pilih kelas yang ingin ditambahkan.", parent=parent)
            return
        try:
            krs.ambil_kelas(int(picked[0]))
        except AppError as err:
            messagebox.showerror("Tambah kelas", str(err), parent=parent)
            return
        except mysql.connector.Error as err:
            messagebox.showerror("Database", str(err), parent=parent)
            return
        muat()

    def lepas():
        picked = selected.selection()
        if not picked:
            messagebox.showwarning("KRS", "Pilih kelas yang ingin dihapus.", parent=parent)
            return
        try:
            krs.hapus_kelas(int(picked[0]))
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Hapus kelas", str(err), parent=parent)
            return
        muat()

    def ajukan():
        if not messagebox.askyesno("Ajukan KRS", "Kirim KRS ini ke dosen PA untuk disetujui?", parent=parent):
            return
        try:
            krs.ajukan()
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Ajukan KRS", str(err), parent=parent)
            return
        messagebox.showinfo("KRS", "KRS berhasil diajukan ke dosen PA.", parent=parent)
        muat()

    add_button = ttk.Button(left, text="Tambahkan ke KRS", command=ambil)
    add_button.pack(anchor="w")
    remove_button = ttk.Button(right, text="Hapus dari KRS", command=lepas)
    remove_button.pack(side="left")
    submit_button = ttk.Button(right, text="Ajukan ke Dosen PA", command=ajukan)
    submit_button.pack(side="right")
    ttk.Button(parent, text="Muat Ulang", command=muat).pack(anchor="w", pady=(10, 0))
    muat()


def _halaman_dosen(parent):
    content = tk.Frame(parent, bg=BG_COLOR)
    content.pack(fill="both", expand=True)
    left = tk.Frame(content, bg=BG_COLOR)
    left.pack(side="left", fill="both", expand=True, padx=(0, 12))
    right = tk.Frame(content, bg=BG_COLOR)
    right.pack(side="left", fill="both", expand=True, padx=(12, 0))

    tk.Label(left, text="Menunggu persetujuan", bg=BG_COLOR, font=("Segoe UI", 12, "bold")).pack(anchor="w")
    cols = ("nim", "nama", "prodi", "semester")
    queue = ttk.Treeview(left, columns=cols, show="headings", height=15)
    for key, label, width in (
        ("nim", "NIM", 90),
        ("nama", "Nama Mahasiswa", 190),
        ("prodi", "Prodi", 130),
        ("semester", "Semester", 90),
    ):
        queue.heading(key, text=label)
        queue.column(key, width=width, anchor="w")
    queue.pack(fill="both", expand=True, pady=(6, 8))

    tk.Label(right, text="Detail KRS", bg=BG_COLOR, font=("Segoe UI", 12, "bold")).pack(anchor="w")
    profile = tk.Label(right, text="Pilih pengajuan untuk melihat detail.", bg=BG_COLOR, justify="left", anchor="w")
    profile.pack(fill="x", pady=(6, 10))
    item_table = ttk.Treeview(right, columns=("kode", "nama", "sks", "kelas"), show="headings", height=12)
    for key, label, width in (
        ("kode", "Kode", 75),
        ("nama", "Mata Kuliah", 190),
        ("sks", "SKS", 45),
        ("kelas", "Kelas", 60),
    ):
        item_table.heading(key, text=label)
        item_table.column(key, width=width, anchor="w")
    item_table.pack(fill="both", expand=True)
    ttk.Label(right, text="Catatan PA (opsional)", bg=BG_COLOR).pack(anchor="w", pady=(10, 2))
    note = ttk.Entry(right)
    note.pack(fill="x", pady=(0, 8))
    selected_detail = {"krs_id": None}
    queue_rows = []

    def muat_antrian():
        nonlocal queue_rows
        for table in (queue, item_table):
            for item in table.get_children():
                table.delete(item)
        profile.config(text="Pilih pengajuan untuk melihat detail.")
        selected_detail["krs_id"] = None
        try:
            queue_rows = krs.daftar_persetujuan()
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Persetujuan KRS", str(err), parent=parent)
            return
        for row in queue_rows:
            queue.insert(
                "",
                "end",
                iid=str(row["krs_id"]),
                values=(row["nim"], row["nama_lengkap"], row["nama_prodi"], row["kode_semester"]),
            )

    def pilih(event=None):
        picked = queue.selection()
        if not picked:
            return
        note.delete(0, "end")
        krs_id = int(picked[0])
        try:
            data = krs.detail_persetujuan(krs_id)
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Detail KRS", str(err), parent=parent)
            return
        selected_detail["krs_id"] = krs_id
        student = data["krs"]
        profile.config(
            text=f"{student['nama_lengkap']} ({student['nim']})\n"
            f"{student['nama_prodi']} · Semester {student['kode_semester']} · Angkatan {student['angkatan']}"
        )
        for row in data["detail"]:
            item_table.insert(
                "",
                "end",
                values=(row["kode_mk"], row["nama_mk"], row["sks"], row["nama_kelas"]),
            )

    def putuskan(status):
        krs_id = selected_detail["krs_id"]
        if krs_id is None:
            messagebox.showwarning("Persetujuan", "Pilih pengajuan KRS terlebih dahulu.", parent=parent)
            return
        try:
            krs.putuskan(krs_id, status, note.get())
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Persetujuan KRS", str(err), parent=parent)
            return
        messagebox.showinfo("Persetujuan KRS", f"KRS {status.lower()}.", parent=parent)
        muat_antrian()

    queue.bind("<<TreeviewSelect>>", pilih)
    buttons = ttk.Frame(right)
    buttons.pack(fill="x", pady=(8, 0))
    ttk.Button(buttons, text="Tolak", command=lambda: putuskan("Ditolak")).pack(side="left")
    ttk.Button(buttons, text="Setujui", command=lambda: putuskan("Disetujui")).pack(side="right")
    ttk.Button(left, text="Muat Ulang", command=muat_antrian).pack(anchor="w")
    muat_antrian()
