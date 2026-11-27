"""Halaman daftar mahasiswa dengan relasi jurusan dan program studi."""
import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector

from assets.colors import BG_COLOR, TEXT_DARK
from backend import auth, mahasiswa
from utils import session
from utils.validators import AppError, nim_input_diizinkan


def tampilkan_mahasiswa(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    tk.Label(
        parent,
        text="Data Mahasiswa",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_DARK,
    ).pack(anchor="w", pady=(0, 14))

    controls = tk.Frame(parent, bg=BG_COLOR)
    controls.pack(fill="x", pady=(0, 12))

    tk.Label(controls, text="Cari nama/NIM", bg=BG_COLOR).pack(side="left")

    keyword = ttk.Entry(controls, width=24)
    keyword.pack(side="left", padx=(6, 12))

    tk.Label(controls, text="Jurusan", bg=BG_COLOR).pack(side="left")

    jurusan_options = [("Semua", None)]

    try:
        jurusan_options.extend(
            (
                f"{row['kode_jurusan']} - {row['nama_jurusan']}",
                row["jurusan_id"],
            )
            for row in auth.daftar_jurusan()
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database", str(err), parent=parent)

    jurusan = ttk.Combobox(
        controls,
        width=25,
        state="readonly",
        values=[option[0] for option in jurusan_options],
    )
    jurusan.current(0)
    jurusan.pack(side="left", padx=(6, 12))

    status_values = ("Semua", "Aktif", "Cuti", "Lulus", "DO", "Keluar")

    status = ttk.Combobox(
        controls,
        width=12,
        state="readonly",
        values=status_values,
    )
    status.current(0)
    status.pack(side="left", padx=(0, 10))

    columns = ("nim", "nama", "prodi", "jurusan", "angkatan", "status")

    table = ttk.Treeview(
        parent,
        columns=columns,
        show="headings",
        height=18,
    )

    labels = {
        "nim": "NIM",
        "nama": "Nama Lengkap",
        "prodi": "Program Studi",
        "jurusan": "Jurusan",
        "angkatan": "Angkatan",
        "status": "Status",
    }

    widths = {
        "nim": 110,
        "nama": 210,
        "prodi": 180,
        "jurusan": 180,
        "angkatan": 80,
        "status": 90,
    }

    for column in columns:
        table.heading(column, text=labels[column])
        table.column(column, width=widths[column], anchor="w")

    table.pack(fill="both", expand=True)

    def muat_data():
        for item in table.get_children():
            table.delete(item)

        selected_jurusan_id = jurusan_options[jurusan.current()][1]
        status_value = status.get()

        try:
            rows = mahasiswa.daftar(
                keyword=keyword.get(),
                jurusan_id=selected_jurusan_id,
                status=status_value if status_value != "Semua" else None,
            )

        except AppError as err:
            messagebox.showerror(
                "Data mahasiswa",
                str(err),
                parent=parent,
            )
            return

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database",
                str(err),
                parent=parent,
            )
            return

        for row in rows:
            table.insert(
                "",
                "end",
                iid=str(row["mahasiswa_id"]),
                values=(
                    row["nim"],
                    row["nama_lengkap"],
                    f"{row['jenjang']} {row['nama_prodi']}",
                    row["nama_jurusan"],
                    row["angkatan"] or "-",
                    row["status_mahasiswa"],
                ),
            )

    ttk.Button(
        controls,
        text="Tampilkan",
        command=muat_data,
    ).pack(side="left")

    def tambah_mahasiswa():
        try:
            jurusan_rows = auth.daftar_jurusan()

        except mysql.connector.Error as err:
            messagebox.showerror("Database", str(err), parent=parent)
            return

        if not jurusan_rows:
            messagebox.showwarning(
                "Registrasi",
                "Tambahkan jurusan dan program studi terlebih dahulu.",
                parent=parent,
            )
            return

        dialog = tk.Toplevel(parent.winfo_toplevel())
        dialog.title("Daftarkan Mahasiswa")
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=18)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        entries = {}
        row_index = 0

        def entry(label, key, secret=False):
            nonlocal row_index

            ttk.Label(form, text=label).grid(
                row=row_index,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=5,
            )

            value = ttk.Entry(
                form,
                width=34,
                show="*" if secret else "",
            )

            if key == "nim":
                validasi = (
                    value.register(nim_input_diizinkan),
                    "%P",
                )
                value.configure(
                    validate="key",
                    validatecommand=validasi,
                )

            value.grid(
                row=row_index,
                column=1,
                sticky="ew",
                pady=5,
            )

            entries[key] = value
            row_index += 1

        entry("NIM / Username (9 digit)", "nim")
        entry("Nama lengkap", "nama")
        entry("Email", "email")
        entry("Password", "password", secret=True)

        ttk.Label(form, text="Jurusan").grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        jurusan_choice = ttk.Combobox(
            form,
            state="readonly",
            values=[
                f"{item['kode_jurusan']} - {item['nama_jurusan']}"
                for item in jurusan_rows
            ],
            width=32,
        )

        jurusan_choice.grid(
            row=row_index,
            column=1,
            sticky="ew",
            pady=5,
        )
        jurusan_choice.current(0)
        row_index += 1

        ttk.Label(form, text="Program studi").grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        prodi_choice = ttk.Combobox(
            form,
            state="readonly",
            width=32,
        )
        prodi_choice.grid(
            row=row_index,
            column=1,
            sticky="ew",
            pady=5,
        )
        row_index += 1

        ttk.Label(form, text="Dosen PA").grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        dosen_choice = ttk.Combobox(
            form,
            state="readonly",
            width=32,
        )
        dosen_choice.grid(
            row=row_index,
            column=1,
            sticky="ew",
            pady=5,
        )
        row_index += 1

        prodi_rows = []
        dosen_rows = []

        def muat_dosen(event=None):
            nonlocal dosen_rows

            idx = prodi_choice.current()
            dosen_rows = []

            if idx < 0 or idx >= len(prodi_rows):
                dosen_choice["values"] = ()
                dosen_choice.set("")
                return

            try:
                dosen_rows = auth.daftar_dosen(
                    prodi_rows[idx]["prodi_id"]
                )

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database",
                    str(err),
                    parent=dialog,
                )
                dosen_choice["values"] = ()
                return

            dosen_choice["values"] = [
                f"{item['nama_lengkap']} "
                f"({item['nidn'] or item['nip'] or item['dosen_id']})"
                for item in dosen_rows
            ]

            if dosen_rows:
                dosen_choice.current(0)
            else:
                dosen_choice.set("")

        def muat_prodi(event=None):
            nonlocal prodi_rows, dosen_rows

            jurusan_index = jurusan_choice.current()

            if jurusan_index < 0:
                prodi_rows = []
                dosen_rows = []
                prodi_choice["values"] = ()
                dosen_choice["values"] = ()
                prodi_choice.set("")
                dosen_choice.set("")
                return

            try:
                prodi_rows = auth.daftar_prodi(
                    jurusan_rows[jurusan_index]["jurusan_id"]
                )

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database",
                    str(err),
                    parent=dialog,
                )
                prodi_rows = []
                dosen_rows = []
                prodi_choice["values"] = ()
                dosen_choice["values"] = ()
                return

            prodi_choice["values"] = [
                f"{item['jenjang']} {item['nama_prodi']}"
                for item in prodi_rows
            ]

            if prodi_rows:
                prodi_choice.current(0)
                muat_dosen()
            else:
                dosen_rows = []
                prodi_choice.set("")
                dosen_choice["values"] = ()
                dosen_choice.set("")

        jurusan_choice.bind(
            "<<ComboboxSelected>>",
            muat_prodi,
        )
        prodi_choice.bind(
            "<<ComboboxSelected>>",
            muat_dosen,
        )

        muat_prodi()

        ttk.Label(form, text="Jenis kelamin").grid(
            row=row_index,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        gender = ttk.Combobox(
            form,
            state="readonly",
            values=("L", "P"),
            width=32,
        )
        gender.grid(
            row=row_index,
            column=1,
            sticky="ew",
            pady=5,
        )
        row_index += 1

        entry("Tanggal lahir (YYYY-MM-DD)", "tanggal_lahir")
        entry("Angkatan", "angkatan")

        def simpan():
            if (
                prodi_choice.current() < 0
                or prodi_choice.current() >= len(prodi_rows)
                or dosen_choice.current() < 0
                or dosen_choice.current() >= len(dosen_rows)
            ):
                messagebox.showerror(
                    "Registrasi",
                    "Pilih program studi yang memiliki dosen PA aktif.",
                    parent=dialog,
                )
                return

            nim = entries["nim"].get().strip()

            try:
                auth.registrasi(
                    username=nim,
                    email=entries["email"].get(),
                    password=entries["password"].get(),
                    nim=nim,
                    nama=entries["nama"].get(),
                    prodi_id=prodi_rows[
                        prodi_choice.current()
                    ]["prodi_id"],
                    dosen_pa_id=dosen_rows[
                        dosen_choice.current()
                    ]["dosen_id"],
                    jenis_kelamin=gender.get(),
                    tanggal_lahir=entries["tanggal_lahir"].get(),
                    angkatan=entries["angkatan"].get(),
                )

            except AppError as err:
                messagebox.showerror(
                    "Registrasi gagal",
                    str(err),
                    parent=dialog,
                )
                return

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database",
                    str(err),
                    parent=dialog,
                )
                return

            messagebox.showinfo(
                "Registrasi",
                f"Akun mahasiswa {nim} berhasil dibuat.",
                parent=dialog,
            )

            dialog.destroy()
            muat_data()

        ttk.Button(
            form,
            text="Simpan Mahasiswa",
            command=simpan,
        ).grid(
            row=row_index,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(14, 0),
        )

    def ubah_mahasiswa():
        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Ubah mahasiswa",
                "Pilih mahasiswa terlebih dahulu.",
                parent=parent,
            )
            return

        try:
            data = mahasiswa.detail(int(selected[0]))
            jurusan_rows = auth.daftar_jurusan()

        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror(
                "Ubah mahasiswa",
                str(err),
                parent=parent,
            )
            return

        dialog = tk.Toplevel(parent.winfo_toplevel())
        dialog.title(f"Ubah Mahasiswa — {data['nim']}")
        dialog.transient(parent.winfo_toplevel())
        dialog.grab_set()

        form = ttk.Frame(dialog, padding=18)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        fields = {}

        def add_entry(label, key, value):
            row = len(fields)

            ttk.Label(form, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=5,
            )

            control = ttk.Entry(form, width=34)
            control.insert(
                0,
                "" if value is None else str(value),
            )
            control.grid(
                row=row,
                column=1,
                sticky="ew",
                pady=5,
            )

            fields[key] = control

        add_entry("Nama lengkap", "nama", data["nama_lengkap"])

        ttk.Label(form, text="Jenis kelamin").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        gender = ttk.Combobox(
            form,
            state="readonly",
            values=("L", "P"),
            width=32,
        )
        gender.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=5,
        )
        gender.set(data["jenis_kelamin"] or "")

        add_entry(
            "Tanggal lahir (YYYY-MM-DD)",
            "tanggal_lahir",
            data["tanggal_lahir"],
        )
        add_entry("Angkatan", "angkatan", data["angkatan"])

        ttk.Label(form, text="Status").grid(
            row=4,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        status_edit = ttk.Combobox(
            form,
            state="readonly",
            values=("Aktif", "Cuti", "Lulus", "DO", "Keluar"),
            width=32,
        )
        status_edit.grid(
            row=4,
            column=1,
            sticky="ew",
            pady=5,
        )
        status_edit.set(data["status_mahasiswa"])

        ttk.Label(form, text="Jurusan").grid(
            row=5,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        jurusan_edit = ttk.Combobox(
            form,
            state="readonly",
            values=[
                f"{item['kode_jurusan']} - {item['nama_jurusan']}"
                for item in jurusan_rows
            ],
            width=32,
        )
        jurusan_edit.grid(
            row=5,
            column=1,
            sticky="ew",
            pady=5,
        )

        ttk.Label(form, text="Program studi").grid(
            row=6,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        prodi_edit = ttk.Combobox(
            form,
            state="readonly",
            width=32,
        )
        prodi_edit.grid(
            row=6,
            column=1,
            sticky="ew",
            pady=5,
        )

        ttk.Label(form, text="Dosen PA").grid(
            row=7,
            column=0,
            sticky="w",
            padx=(0, 12),
            pady=5,
        )

        dosen_edit = ttk.Combobox(
            form,
            state="readonly",
            width=32,
        )
        dosen_edit.grid(
            row=7,
            column=1,
            sticky="ew",
            pady=5,
        )

        prodi_rows = []
        dosen_rows = []

        def load_dosen(event=None):
            nonlocal dosen_rows

            idx = prodi_edit.current()
            dosen_rows = []

            if idx < 0 or idx >= len(prodi_rows):
                dosen_edit["values"] = ()
                dosen_edit.set("")
                return

            try:
                dosen_rows = auth.daftar_dosen(
                    prodi_rows[idx]["prodi_id"]
                )

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database",
                    str(err),
                    parent=dialog,
                )
                dosen_edit["values"] = ()
                return

            dosen_edit["values"] = [
                f"{item['nama_lengkap']} "
                f"({item['nidn'] or item['nip'] or item['dosen_id']})"
                for item in dosen_rows
            ]

            current = next(
                (
                    i
                    for i, item in enumerate(dosen_rows)
                    if item["dosen_id"] == data["dosen_pa_id"]
                ),
                0 if dosen_rows else -1,
            )

            if current >= 0:
                dosen_edit.current(current)
            else:
                dosen_edit.set("")

        def load_prodi(event=None):
            nonlocal prodi_rows, dosen_rows

            idx = jurusan_edit.current()

            if idx < 0 or idx >= len(jurusan_rows):
                prodi_rows = []
                dosen_rows = []
                prodi_edit["values"] = ()
                dosen_edit["values"] = ()
                prodi_edit.set("")
                dosen_edit.set("")
                return

            try:
                prodi_rows = auth.daftar_prodi(
                    jurusan_rows[idx]["jurusan_id"]
                )

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database",
                    str(err),
                    parent=dialog,
                )
                prodi_rows = []
                dosen_rows = []
                prodi_edit["values"] = ()
                dosen_edit["values"] = ()
                return

            prodi_edit["values"] = [
                f"{row['jenjang']} {row['nama_prodi']}"
                for row in prodi_rows
            ]

            current = next(
                (
                    i
                    for i, row in enumerate(prodi_rows)
                    if row["prodi_id"] == data["prodi_id"]
                ),
                0 if prodi_rows else -1,
            )

            if current >= 0:
                prodi_edit.current(current)
                load_dosen()
            else:
                dosen_rows = []
                prodi_edit.set("")
                dosen_edit["values"] = ()
                dosen_edit.set("")

        jurusan_edit.bind(
            "<<ComboboxSelected>>",
            load_prodi,
        )
        prodi_edit.bind(
            "<<ComboboxSelected>>",
            load_dosen,
        )

        jurusan_index = next(
            (
                i
                for i, row in enumerate(jurusan_rows)
                if row["jurusan_id"] == data["jurusan_id"]
            ),
            0 if jurusan_rows else -1,
        )

        if jurusan_index >= 0:
            jurusan_edit.current(jurusan_index)
            load_prodi()

        def save_changes():
            if (
                prodi_edit.current() < 0
                or prodi_edit.current() >= len(prodi_rows)
                or dosen_edit.current() < 0
                or dosen_edit.current() >= len(dosen_rows)
            ):
                messagebox.showerror(
                    "Ubah mahasiswa",
                    "Pilih prodi dan dosen PA aktif.",
                    parent=dialog,
                )
                return

            try:
                mahasiswa.ubah_profil(
                    mahasiswa_id=data["mahasiswa_id"],
                    nama=fields["nama"].get(),
                    prodi_id=prodi_rows[
                        prodi_edit.current()
                    ]["prodi_id"],
                    dosen_pa_id=dosen_rows[
                        dosen_edit.current()
                    ]["dosen_id"],
                    jenis_kelamin=gender.get(),
                    tanggal_lahir=fields["tanggal_lahir"].get(),
                    angkatan=fields["angkatan"].get(),
                    status=status_edit.get(),
                    tempat_lahir=data["tempat_lahir"],
                    agama=data["agama"],
                    nik=data["nik"],
                    alamat=data["alamat"],
                    no_hp=data["no_hp"],
                    nama_ayah=data["nama_ayah"],
                    nama_ibu=data["nama_ibu"],
                )

            except AppError as err:
                messagebox.showerror(
                    "Ubah mahasiswa",
                    str(err),
                    parent=dialog,
                )
                return

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database",
                    str(err),
                    parent=dialog,
                )
                return

            dialog.destroy()
            muat_data()

        ttk.Button(
            form,
            text="Simpan Perubahan",
            command=save_changes,
        ).grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(14, 0),
        )

    user = session.get_user()

    if user and user.get("role") == "admin":
        ttk.Button(
            controls,
            text="Tambah Mahasiswa",
            command=tambah_mahasiswa,
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            controls,
            text="Ubah Mahasiswa",
            command=ubah_mahasiswa,
        ).pack(side="left", padx=(8, 0))

    def lihat_detail(event=None):
        selected = table.selection()

        if not selected:
            return

        try:
            data = mahasiswa.detail(int(selected[0]))

        except (AppError, mysql.connector.Error) as err:
            messagebox.showerror(
                "Detail mahasiswa",
                str(err),
                parent=parent,
            )
            return

        messagebox.showinfo(
            "Detail Mahasiswa",
            f"Nama: {data['nama_lengkap']}\n"
            f"NIM: {data['nim']}\n"
            f"Prodi: {data['jenjang']} {data['nama_prodi']}\n"
            f"Jurusan: {data['nama_jurusan']}\n"
            f"Dosen PA: {data['nama_dosen_pa']}\n"
            f"Jenis kelamin: {data['jenis_kelamin']}\n"
            f"Angkatan: {data['angkatan']}\n"
            f"Status: {data['status_mahasiswa']}",
            parent=parent,
        )

    table.bind("<Double-1>", lihat_detail)
    muat_data()
