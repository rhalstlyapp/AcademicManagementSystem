"""Halaman pembacaan nilai final berdasarkan mahasiswa."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, TEXT_DARK
from backend import mahasiswa, nilai
from utils.validators import AppError


def tampilkan_nilai(parent, user):
    for widget in parent.winfo_children():
        widget.destroy()
    tk.Label(
        parent,
        text="Nilai Mahasiswa",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 12))

    selected_id = user.get("mahasiswa_id")
    if user["role"] in ("admin", "dosen"):
        try:
            students = mahasiswa.daftar()
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Data mahasiswa", str(err), parent=parent)
            return
        if not students:
            tk.Label(parent, text="Belum ada mahasiswa.", bg=BG_COLOR).pack(anchor="w")
            return
        choices = ttk.Combobox(
            parent,
            state="readonly",
            width=55,
            values=[f"{row['nim']} - {row['nama_lengkap']}" for row in students],
        )
        choices.pack(anchor="w", pady=(0, 12))
        choices.current(0)
        ids = [row["mahasiswa_id"] for row in students]
    else:
        choices = None
        ids = []

    cols = ("semester", "kode", "mata_kuliah", "sks", "angka", "huruf", "status")
    table = ttk.Treeview(parent, columns=cols, show="headings", height=18)
    headings = (
        ("semester", "Semester", 100),
        ("kode", "Kode", 95),
        ("mata_kuliah", "Mata Kuliah", 260),
        ("sks", "SKS", 55),
        ("angka", "Nilai", 75),
        ("huruf", "Huruf", 65),
        ("status", "Status", 120),
    )
    for col, label, width in headings:
        table.heading(col, text=label)
        table.column(col, width=width, anchor="w")
    table.pack(fill="both", expand=True)

    def muat(event=None):
        target_id = selected_id
        if choices is not None:
            target_id = ids[choices.current()]
        for item in table.get_children():
            table.delete(item)
        try:
            rows = nilai.daftar(target_id)
        except AppError as err:
            messagebox.showerror("Nilai", str(err), parent=parent)
            return
        except mysql.connector.Error as err:
            messagebox.showerror("Database", str(err), parent=parent)
            return
        for row in rows:
            table.insert(
                "",
                "end",
                values=(
                    row["kode_semester"],
                    row["kode_mk"],
                    row["nama_mk"],
                    row["sks"],
                    row["nilai_akhir"],
                    row["huruf_mutu"],
                    row["status_kelulusan"],
                ),
            )

    ttk.Button(parent, text="Muat Nilai", command=muat).pack(anchor="w", pady=(8, 0))
    if choices is not None:
        choices.bind("<<ComboboxSelected>>", muat)

    if user["role"] == "dosen":
        def buka_input_nilai():
            try:
                assignments = nilai.daftar_krs_untuk_input()
            except (AppError, mysql.connector.Error) as err:
                messagebox.showerror("Input Nilai", str(err), parent=parent)
                return
            if not assignments:
                messagebox.showinfo("Input Nilai", "Tidak ada KRS disetujui yang menunggu nilai.", parent=parent)
                return
            dialog = tk.Toplevel(parent.winfo_toplevel())
            dialog.title("Input Nilai Akhir")
            dialog.transient(parent.winfo_toplevel())
            dialog.grab_set()
            form = ttk.Frame(dialog, padding=18)
            form.pack(fill="both", expand=True)
            ttk.Label(form, text="Mahasiswa dan mata kuliah").pack(anchor="w")
            selection = ttk.Combobox(
                form,
                state="readonly",
                width=64,
                values=[
                    f"{row['nim']} - {row['nama_lengkap']} | {row['kode_mk']} "
                    f"{row['nama_mk']} | {row['kode_semester']}"
                    for row in assignments
                ],
            )
            selection.pack(fill="x", pady=(4, 12))
            selection.current(0)
            ttk.Label(form, text="Nilai akhir (0-100)").pack(anchor="w")
            score = ttk.Entry(form, width=20)
            score.pack(anchor="w", pady=(4, 8))
            preview = ttk.Label(form, text="")
            preview.pack(anchor="w", pady=(0, 8))

            def preview_score():
                try:
                    result = nilai.pratinjau(score.get())
                except (AppError, mysql.connector.Error) as err:
                    messagebox.showerror("Pratinjau nilai", str(err), parent=dialog)
                    return
                preview.config(
                    text=f"Nilai akhir: {result['nilai_akhir']}  |  "
                    f"Huruf: {result['huruf_mutu']}  |  Bobot: {result['bobot_mutu']}"
                )

            def save_score():
                assignment = assignments[selection.current()]
                try:
                    nilai.simpan(assignment["krs_detail_id"], score.get())
                except (AppError, mysql.connector.Error) as err:
                    messagebox.showerror("Simpan nilai", str(err), parent=dialog)
                    return
                target_student_id = assignment["mahasiswa_id"]
                if choices is not None and target_student_id in ids:
                    choices.current(ids.index(target_student_id))
                dialog.destroy()
                muat()

            buttons = ttk.Frame(form)
            buttons.pack(fill="x", pady=(8, 0))
            ttk.Button(buttons, text="Pratinjau", command=preview_score).pack(side="left")
            ttk.Button(buttons, text="Finalisasi Nilai", command=save_score).pack(side="right")

        ttk.Button(parent, text="Input Nilai", command=buka_input_nilai).pack(anchor="w", pady=(8, 0))
    muat()
