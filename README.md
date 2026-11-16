# Academic Management System (SIAKAD)

Sistem Informasi Akademik perguruan tinggi berbasis Python dan MySQL, dengan akses berbasis peran (Admin, Dosen, Mahasiswa).

## Fitur

1 Login & manajemen user
2 Dashboard
3 Manajemen mahasiswa
4 Manajemen mata kuliah
5 Manajemen nilai
6 Perhitungan IPS/IPK
7 Transkrip nilai
8 Search & filter
9 Validasi data
10 Logout & log aktivitas

## Struktur Proyek

```
AcademicManagementSystem/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── database/
│   ├── connection.py
│   ├── schema.sql              ← ditulis ulang (6 tabel)
│   ├── seed.sql                ← ditulis ulang
│   ├── triggers_views.sql      ← diisi (v_ips, v_ipk, v_transkrip)
│   └── create_admin.py         ← (opsional)
│
├── backend/
│   ├── prodi.py
│   ├── mahasiswa.py
│   ├── mata_kuliah.py
│   ├── semester.py
│   ├── nilai.py                ← input nilai + skala nilai
│   ├── ipk.py                  ← hitung IPS/IPK + transkrip
│   ├── auth.py                 ← (opsional)
│   └── log.py                  ← (opsional)
│
├── frontend/
│   ├── login_page.py           ← (opsional)
│   ├── dashboard_page.py       ← ringkasan sederhana (opsional)
│   ├── mahasiswa_page.py
│   ├── akademik_master_page.py ← prodi, semester, mata kuliah
│   ├── nilai_page.py
│   └── transkrip_page.py       ← IPS per semester, IPK, transkrip
│
├── utils/
│   ├── validators.py           ← nilai 0–100, format NIM
│   ├── security.py             ← (opsional)
│   ├── session.py              ← (opsional)
│   └── permissions.py          ← (opsional)
│
├── docs/
│   ├── erd_ipk.png
│   └── archive/erd_siakad.png  ← ERD versi lengkap
│
└── assets/
    ├── logo.png
    └── icons/
```

## ERD

![ERD SIAKAD](docs/erd_ipk.png)

Rancangan database dinormalisasi hingga **3NF**.

## Teknologi

- Python 3.10+
- MySQL 8
- Library: lihat `requirements.txt`

## Instalasi

1. **Clone repository**

   ```bash
   git clone https://github.com/<username>/AcademicManagementSystem.git
   cd AcademicManagementSystem
   ```

2. **Buat virtual environment dan install dependensi**

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # macOS / Linux
   pip install -r requirements.txt
   ```

3. **Siapkan database**

   ```sql
   CREATE DATABASE siakad CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

   Lalu import berurutan:

   ```bash
   mysql -u <user> -p siakad < database/schema.sql
   mysql -u <user> -p siakad < database/seed.sql
   mysql -u <user> -p siakad < database/triggers_views.sql
   ```

4. **Konfigurasi environment**

   ```bash
   copy .env.example .env         # Windows
   cp .env.example .env           # macOS / Linux
   ```

   Isi `DB_USER`, `DB_PASSWORD`, dan nilai lainnya di file `.env`.

5. **Jalankan aplikasi**
   ```bash
   python main.py
   ```

## Akun Awal

Akun admin awal dibuat oleh `database/seed.sql`. Ganti password default segera setelah login pertama.

## Alur Pengembangan

- Branch utama: `main`
- Satu branch per fitur: `feature/krs`, `feature/nilai`, dst.
- Pesan commit: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`

## Status

Dalam pengembangan.
