"""Halaman admin untuk membuat kelas dan menetapkan dosen pengajar."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, TEXT_DARK
from backend import dosen, kelas, mata_kuliah, semester
from utils.validators import AppError


def tampilkan_kelas(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent,
        text="Kelas Kuliah",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 12))
    try:
        semester_rows = semester.daftar()
    except (AppError, mysql.connector.Error) as err:
        messagebox.showerror("Semester", str(err), parent=parent)
        return
    if not semester_rows:
        tk.Label(parent, text="Tambahkan semester terlebih dahulu.", bg=BG_COLOR).pack(anchor="w")
        return

    filters = tk.Frame(parent, bg=BG_COLOR)
    filters.pack(fill="x", pady=(0, 10))
    semester_filter = ttk.Combobox(
        filters,
        state="readonly",
        width=20,
        values=["Semua semester"]
        + [f"{row['kode_semester']} — {row['tahun_akademik']}" for row in semester_rows],
    )
    semester_filter.pack(side="left", padx=(0, 8))
    semester_filter.current(0)
    ttk.Button(filters, text="Muat", command=lambda: muat_data()).pack(side="left")

    columns = ("semester", "kode", "mata_kuliah", "prodi", "kelas", "kuota", "terdaftar", "dosen")
    table = ttk.Treeview(parent, columns=columns, show="headings", height=18)
    for key, label, width in (
        ("semester", "Semester", 115),
        ("kode", "Kode MK", 90),
        ("mata_kuliah", "Mata Kuliah", 200),
        ("prodi", "Program Studi", 155),
        ("kelas", "Kelas", 60),
        ("kuota", "Kuota", 65),
        ("terdaftar", "Terdaftar", 85),
        ("dosen", "Dosen Pengajar", 190),
    ):
        table.heading(key, text=label)
        table.column(key, width=width, anchor="w")
    table.pack(fill="both", expand=True)

    def muat_data():
        for item in table.get_children():
            table.delete(item)
        selected = semester_filter.current()
        semester_id = semester_rows[selected - 1]["semester_id"] if 0 < selected <= len(semester_rows) else None
        try:
            rows = kelas.daftar(semester_id=semester_id)
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Kelas", str(err), parent=parent)
            return
        for row in rows:
            table.insert(
                "",
                "end",
                iid=str(row["kelas_id"]),
                values=(
                    row["kode_semester"],
                    row["kode_mk"],
                    row["nama_mk"],
                    row["nama_prodi"],
                    row["nama_kelas"],
                    row["kuota"],
                    row["jumlah_terdaftar"],
                    row["dosen_pengajar"] or "-",
                ),
            )

    def tambah_kelas():
        try:
            course_rows = mata_kuliah.daftar()
            lecturer_rows = dosen.daftar(status="Aktif")
        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror("Data kelas", str(err), parent=parent)
            return
        if not course_rows:
            messagebox.showwarning("Kelas", "Belum ada mata kuliah. Tambahkan mata kuliah terlebih dahulu.", parent=parent)
            return
        if not lecturer_rows:
            messagebox.showwarning("Kelas", "Tambahkan dosen aktif terlebih dahulu.", parent=parent)
            return

        dialog = tk.Toplevel(parent.winfo_toplevel())
        dialog.title("Tambah Kelas")
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()
        form = ttk.Frame(dialog, padding=18)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        def label(row, text):
            ttk.Label(form, text=text).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)

        label(0, "Mata kuliah")
        course_choice = ttk.Combobox(
            form,
            state="readonly",
            width=46,
            values=[
                f"{row['kode_mk']} — {row['nama_mk']} ({row['nama_prodi']}, {row['nama_kurikulum']})"
                for row in course_rows
            ],
        )
        course_choice.grid(row=0, column=1, sticky="ew", pady=6)
        course_choice.current(0)

        label(1, "Semester")
        semester_choice = ttk.Combobox(
            form,
            state="readonly",
            width=46,
            values=[f"{row['kode_semester']} — {row['tahun_akademik']}" for row in semester_rows],
        )
        semester_choice.grid(row=1, column=1, sticky="ew", pady=6)
        semester_choice.current(0)

        label(2, "Nama kelas")
        class_name = ttk.Entry(form, width=48)
        class_name.grid(row=2, column=1, sticky="ew", pady=6)
        class_name.insert(0, "A")

        label(3, "Kuota")
        capacity = ttk.Entry(form, width=48)
        capacity.grid(row=3, column=1, sticky="ew", pady=6)
        capacity.insert(0, "30")

        label(4, "Dosen pengajar")
        lecturer_choice = ttk.Combobox(
            form,
            state="readonly",
            width=46,
            values=[
                f"{row['nama_lengkap']} — {row['kode_prodi']}"
                for row in lecturer_rows
            ],
        )
        lecturer_choice.grid(row=4, column=1, sticky="ew", pady=6)
        lecturer_choice.current(0)

        def simpan():
            try:
                kelas.tambah(
                    mk_id=course_rows[course_choice.current()]["mk_id"],
                    semester_id=semester_rows[semester_choice.current()]["semester_id"],
                    nama_kelas=class_name.get(),
                    kuota=capacity.get(),
                    dosen_id=lecturer_rows[lecturer_choice.current()]["dosen_id"],
                )
            except AppError as err:
                messagebox.showerror("Tambah kelas", str(err), parent=dialog)
                return
            except mysql.connector.Error as err:
                messagebox.showerror("Database", str(err), parent=dialog)
                return
            dialog.destroy()
            muat_data()

        ttk.Button(form, text="Simpan Kelas", command=simpan).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )

    ttk.Button(filters, text="Tambah Kelas", command=tambah_kelas).pack(side="right")
    muat_data()
