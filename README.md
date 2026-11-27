# Academic Management System (SIAKAD)

**Academic Management System (SIAKAD)** adalah aplikasi desktop berbasis **Python** dan **MySQL** dengan antarmuka grafis (**CustomTkinter**) yang digunakan untuk mengelola data akademik mahasiswa, nilai, serta informasi **IPS** dan **IPK**.

Project ini dikembangkan sebagai bagian dari tugas **UAS mata kuliah Basis Data**.

---

## Tentang Project

Academic Management System dirancang untuk membantu pengelolaan data akademik secara terstruktur melalui aplikasi GUI yang memisahkan lapisan tampilan, logika aplikasi, utilitas, dan basis data.

Sistem memiliki **dua role utama**:

- **Admin** — mengelola data master akademik, akun mahasiswa, serta input/pengelolaan nilai.
- **Mahasiswa** — melihat profil akademik, nilai mata kuliah, IPS, IPK, dan transkrip akademik secara mandiri.

---

## Fitur Utama

### Autentikasi & Hak Akses

- Login pengguna berbasis akun.
- Kontrol akses berbasis role (**Admin** dan **Mahasiswa**).
- Penyimpanan password aman menggunakan *hashing* (`bcrypt`).
- Manajemen *session* pengguna untuk mengatur navigasi dan hak akses halaman.

### Fitur Admin

- Mengelola data **Mahasiswa**.
- Mengelola data **Program Studi**.
- Mengelola data **Mata Kuliah**.
- Mengelola data **Semester Akademik**.
- Mengelola **Data Nilai** mahasiswa.
- Mengelola **Akun Mahasiswa**.

### Fitur Mahasiswa

- Melihat informasi profil dan status akademik.
- Melihat daftar nilai per mata kuliah.
- Melihat **IPS** (Indeks Prestasi Semester).
- Melihat **IPK** (Indeks Prestasi Kumulatif).
- Melihat **Transkrip Akademik**.

### Pengelolaan Nilai

Sistem mendukung pencatatan komponen penilaian, perhitungan nilai akhir, konversi nilai angka ke huruf, serta kalkulasi IPS dan IPK.

| Komponen Penilaian | Bobot |
| :--- | :---: |
| Tugas | **30%** |
| UTS | **30%** |
| UAS | **40%** |

---

## Arsitektur Database

Database menggunakan **MySQL** dengan desain relasional serta penerapan berbagai aturan integritas data:

- **Primary Key** & **Foreign Key**
- **Unique Constraint** & **Check Constraint**
- **Trigger** & **View**
- **Generated Column**

### Tabel Utama

| Tabel | Fungsi |
| :--- | :--- |
| `program_studi` | Menyimpan data program studi |
| `mahasiswa` | Menyimpan data mahasiswa |
| `users` | Menyimpan akun pengguna dan role |
| `mata_kuliah` | Menyimpan data mata kuliah |
| `semester_akademik` | Menyimpan data semester akademik |
| `skala_nilai` | Menyimpan acuan skala dan bobot nilai |
| `nilai` | Menyimpan nilai mahasiswa dan hasil kalkulasi |

---

# Struktur Project

```text
AcademicManagementSystem/
├── assets/
│   ├── colors.py
│   └── styles.py
│
├── backend/
│   ├── auth.py
│   ├── dashboard.py
│   ├── dosen.py
│   ├── ipk.py
│   ├── jurusan.py
│   ├── kelas.py
│   ├── prodi.py
│   ├── mahasiswa.py
│   ├── mata_kuliah.py
│   ├── semester.py
│   ├── nilai.py
│   ├── skala_nilai.py
│   └── tugas.py
│
├── database/
│   ├── connection.py
│   ├── create_admin.py
│   ├── create_tugas_mahasiswa.sql
│   ├── migrate_fakultas_to_jurusan.sql
│   ├── migrate_student_public_registration.sql
│   ├── schema.sql
│   ├── seed.sql
│   ├── triggers_views.sql
│   └── seed_jurusan_prodi.sql
│
├── docs/
│   └── erd_ipk.png
│
├── frontend/
│   ├── dosen.py
│   ├── dosen_page.py
│   ├── main_window.py
│   ├── login_page.py
│   ├── mahasiswa_page.py
│   ├── akademik_master_page.py
│   ├── nilai_page.py
│   ├── pengajaran.py
│   ├── tugas_page.py
│   └── transkrip_page.py
│
├── utils/
│   ├── recent_accounts.py
│   ├── validators.py
│   ├── security.py
│   ├── session.py
│   └── permissions.py
│
├── .env.example
├── .gitignore
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

### Pembagian Layer

| Folder | Tanggung Jawab |
| :--- | :--- |
| `frontend/` | Antarmuka pengguna / GUI aplikasi menggunakan CustomTkinter |
| `backend/` | Logika bisnis dan operasi query ke database |
| `database/` | Koneksi database, skema tabel, seed data, trigger, view, dan script pembuatan akun admin |
| `utils/` | Modul pendukung seperti validasi input, keamanan, manajemen session, dan permission |
| `assets/` | Aset visual atau resource pendukung tampilan aplikasi |
| `docs/` | Dokumentasi project, termasuk diagram ERD |

---

## Teknologi yang Digunakan

- **Python 3.10+**
- **CustomTkinter**
- **MySQL 8.0.16+**
- **mysql-connector-python**
- **bcrypt**
- **python-dotenv**

Daftar lengkap dependency tersedia pada berkas `requirements.txt`.

---

## Instalasi & Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/rhalstlyapp/AcademicManagementSystem.git
cd AcademicManagementSystem
```

### 2. Buat & Aktifkan Virtual Environment

Buat virtual environment:

```bash
python -m venv venv
```

Aktifkan pada Windows:

```bash
venv\Scripts\activate
```

Install seluruh dependency:

```bash
pip install -r requirements.txt
```

### 3. Setup Database MySQL

Pastikan layanan MySQL sudah berjalan, lalu jalankan file SQL di folder `database/` sesuai urutan berikut:

1. `schema.sql` — membuat struktur tabel dan constraint dari awal.
2. `seed.sql` — mengisi data awal.
3. `triggers_views.sql` — membuat trigger dan view.

### 4. Konfigurasi Environment

Salin berkas `.env.example` menjadi `.env`, lalu sesuaikan kredensial database lokal:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=siakad
DB_USER=root
DB_PASSWORD=
```

> **Catatan:** Jangan mengunggah berkas `.env` ke repository publik.

### 5. Membuat Akun Admin

Setelah database siap, jalankan:

```bash
python database/create_admin.py
```

Password admin akan diminta secara interaktif saat script dijalankan dan tidak disimpan secara *hardcoded* di dalam kode sumber.

Akun mahasiswa dapat dibuat sesuai alur yang tersedia pada aplikasi.

### 6. Menjalankan Aplikasi

```bash
python main.py
```

Aplikasi akan menampilkan halaman login terlebih dahulu sebelum mengarahkan pengguna sesuai role.

---

## Alur Sistem

```text
                ┌──────────────┐
                │    Login     │
                └──────┬───────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
          Admin             Mahasiswa
              │                 │
              ▼                 ▼
       Kelola Data         Lihat Data
       Akademik            Akademik
              │                 │
              ▼                 ▼
        Input Nilai        Nilai / IPK
              │
              ▼
        Database MySQL
```

---

## Dokumentasi & ERD

Diagram relasi entitas (**ERD**) dapat dilihat pada:

```text
docs/erd_ipk.png
```

ERD ini menggambarkan relasi antar entitas:

- `program_studi`
- `mahasiswa`
- `users`
- `mata_kuliah`
- `semester_akademik`
- `skala_nilai`
- `nilai`

Dokumentasi tambahan tersedia di folder `docs/`.

---

## Keamanan

Project menerapkan beberapa mekanisme keamanan, antara lain:

- Hashing password menggunakan **bcrypt**.
- Pembatasan akses fitur berdasarkan **role** dan **session**.
- Pengelolaan konfigurasi sensitif melalui environment variables (`.env`).
- Pemisahan antara layer `frontend`, `backend`, `database`, dan `utils`.
- Validasi data pada sisi aplikasi maupun database.

---

## Panduan Kontribusi & Git Workflow

Project dikembangkan secara kolaboratif melalui GitHub dengan branch utama:

```text
main
```

Gunakan branch terpisah untuk pengembangan fitur atau perbaikan bug sebelum melakukan merge ke `main`.

Contoh nama branch:

```text
feature/login
feature/nilai
feature/ipk
fix/register
fix/database
```

Contoh format pesan commit:

```text
feat: menambahkan fitur login
fix: memperbaiki validasi register
docs: memperbarui README
refactor: merapikan backend
```

---

## Status & Lisensi

**Status:** Sedang dalam tahap pengembangan aktif. Fitur maupun struktur berkas dapat menyesuaikan seiring integrasi tim.

**Lisensi:** Dibuat untuk keperluan pembelajaran dan tugas akademik.
