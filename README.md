# Academic Management System (SIAKAD): Nilai & IPK

Aplikasi desktop berbasis Python (GUI) dan MySQL untuk mengelola nilai mahasiswa dan menghitung IPS/IPK. Pengguna wajib login. Dibuat sebagai proyek UAS mata kuliah Basis Data.

## Fitur

- Login admin, dosen, dan mahasiswa memakai username/NIM serta password
- Pembuatan akun dosen dan mahasiswa oleh admin
- Manajemen data mahasiswa, dosen, jurusan, program studi, mata kuliah, dan semester
- Mahasiswa mengisi KRS dan dosen PA menyetujui atau menolaknya
- Input dan finalisasi nilai oleh dosen pada kelas yang diajar
- Konversi nilai angka ke huruf mutu melalui skala nilai yang dapat diubah
- Perhitungan **IPS** per semester dan **IPK** menggunakan VIEW
- Transkrip nilai beserta status kelulusan
- Pencarian dan filter data
- Validasi data lewat constraint dan trigger

Bobot nilai akhir yang dipakai: tugas 30%, UTS 30%, UAS 40%. Untuk mata kuliah yang diulang, IPK memakai nilai terbaik.

## Hak Akses

| Fitur                                                      | Admin           | Dosen             | Mahasiswa              |
| ---------------------------------------------------------- | --------------- | ----------------- | ---------------------- |
| Kelola akun dosen dan mahasiswa                            | ya              | tidak             | tidak                  |
| Kelola data master (jurusan, prodi, mata kuliah, semester) | ya              | tidak             | tidak                  |
| Kelola KRS                                                  | tidak           | setujui KRS PA    | pilih kelas            |
| Input nilai                                                | tidak           | kelas yang diajar | tidak                  |
| Lihat transkrip dan IPK                                    | semua mahasiswa | semua mahasiswa   | hanya miliknya sendiri |

Pembatasan "hanya miliknya sendiri" ditegakkan di lapisan backend, bukan hanya dengan menyembunyikan menu.

## Catatan Keamanan

Password untuk akun admin, dosen, dan mahasiswa disimpan sebagai hash bcrypt pada tabel `users`. Mahasiswa hanya dapat melihat transkrip miliknya; nilai hanya dapat difinalisasi oleh dosen yang mengajar kelas terkait.

## Desain Database

Database `siakad` terdiri dari tabel akademik yang saling terhubung dengan foreign key dan dinormalisasi hingga **3NF**.

| Tabel               | Fungsi                                               |
| ------------------- | ---------------------------------------------------- |
| `jurusan`           | Data jurusan                                         |
| `program_studi`     | Program studi, berada di bawah satu jurusan          |
| `mahasiswa`         | Biodata mahasiswa; **NIM adalah primary key**        |
| `admin`             | Akun admin (username dan hash password)              |
| `mata_kuliah`       | Kode, nama, dan SKS                                  |
| `semester_akademik` | Daftar semester                                      |
| `skala_nilai`       | Huruf mutu, bobot mutu, dan rentang nilai            |
| `nilai`             | Nilai per mahasiswa (NIM), mata kuliah, dan semester |

### ERD

Keterangan: `PK` primary key, `FK` foreign key, `UK` unique. Teks dalam tanda kutip adalah constraint atau aturan pada kolom tersebut.

```mermaid
erDiagram
    jurusan ||--o{ program_studi : "menaungi"
    program_studi ||--o{ mahasiswa : "memiliki"
    mahasiswa ||--o{ nilai : "memperoleh"
    mata_kuliah ||--o{ nilai : "dinilai dalam"
    semester_akademik ||--o{ nilai : "periode"
    skala_nilai ||..o{ nilai : "konversi lewat rentang nilai"

    jurusan {
        int jurusan_id PK "AUTO_INCREMENT"
        varchar kode_jurusan UK "NOT NULL"
        varchar nama_jurusan "NOT NULL"
    }
    program_studi {
        int prodi_id PK "AUTO_INCREMENT"
        int jurusan_id FK "NOT NULL"
        varchar kode_prodi UK "NOT NULL"
        varchar nama_prodi "NOT NULL"
        enum jenjang "D3, D4, S1, S2, S3"
    }
    mahasiswa {
        varchar nim PK "identitas dan pengganti password"
        int prodi_id FK "NOT NULL"
        varchar nama_lengkap "NOT NULL"
        enum jenis_kelamin "boleh NULL"
        date tanggal_lahir "boleh NULL"
        smallint angkatan "boleh NULL, CHECK 1990 sampai 2100"
        enum status_mahasiswa "default Aktif"
        datetime terdaftar_pada "default sekarang"
    }
    admin {
        int admin_id PK "AUTO_INCREMENT"
        varchar username UK "NOT NULL"
        varchar password_hash "hash bcrypt"
        boolean is_active "default TRUE"
        datetime last_login_at "boleh NULL"
        datetime created_at "default sekarang"
    }
    mata_kuliah {
        int mk_id PK "AUTO_INCREMENT"
        varchar kode_mk UK "NOT NULL"
        varchar nama_mk "NOT NULL"
        tinyint sks "CHECK 1 sampai 6"
    }
    semester_akademik {
        int semester_id PK "AUTO_INCREMENT"
        char kode_semester UK "contoh 20251"
        varchar tahun_akademik "contoh 2025/2026"
        enum jenis "Ganjil, Genap, Pendek"
    }
    skala_nilai {
        smallint skala_id PK "AUTO_INCREMENT"
        char huruf_mutu UK "A sampai E"
        decimal bobot_mutu "CHECK 0 sampai 4"
        decimal nilai_min "CHECK 0 sampai 100"
        decimal nilai_max "CHECK min kurang dari max"
        boolean is_lulus "NOT NULL"
    }
    nilai {
        int nilai_id PK "AUTO_INCREMENT"
        varchar nim FK "UNIQUE gabungan, ON UPDATE CASCADE"
        int mk_id FK "UNIQUE gabungan"
        int semester_id FK "UNIQUE gabungan"
        decimal nilai_tugas "CHECK 0 sampai 100"
        decimal nilai_uts "CHECK 0 sampai 100"
        decimal nilai_uas "CHECK 0 sampai 100"
        decimal nilai_akhir "turunan 30, 30, 40"
    }
```

Cara membaca relasi: `||` tepat satu, `o|` nol atau satu, `o{` nol atau banyak. Garis putus-putus berarti relasi logis tanpa foreign key. Tabel `admin` berdiri sendiri karena admin tidak terkait dengan data mahasiswa. Versi gambar tersedia di [docs/erd_ipk.png](docs/erd_ipk.png).

### Aturan dan constraint

| Aturan                                                                                 | Cara penerapan                                    |
| -------------------------------------------------------------------------------------- | ------------------------------------------------- |
| NIM adalah identitas unik mahasiswa                                                    | `PRIMARY KEY (nim)` pada `mahasiswa`              |
| Mengganti NIM otomatis memindahkan nilainya                                            | `FOREIGN KEY ... ON UPDATE CASCADE` pada `nilai`  |
| Satu mahasiswa hanya punya satu nilai per mata kuliah per semester                     | `UNIQUE (nim, mk_id, semester_id)` pada `nilai`   |
| Nilai tugas, UTS, UAS harus 0 sampai 100                                               | `CHECK` pada `nilai`                              |
| Nilai akhir selalu konsisten dengan komponennya                                        | _generated column_: tugas 30% + UTS 30% + UAS 40% |
| Kode jurusan, prodi, mata kuliah, dan semester serta username admin tidak boleh kembar | `UNIQUE`                                          |
| SKS antara 1 dan 6                                                                     | `CHECK` pada `mata_kuliah`                        |
| Nilai baru hanya untuk mahasiswa berstatus Aktif                                       | trigger `trg_nilai_cek_status_bi`                 |
| Mahasiswa berstatus DO atau Keluar tidak dapat login                                   | validasi di `backend/auth.py`                     |
| IPS, IPK, dan transkrip dihitung tanpa menyimpan data ganda                            | `VIEW`: `v_ips`, `v_ipk`, `v_transkrip`           |

### Catatan desain

- `nilai_akhir` adalah kolom turunan yang dihitung database dari nilai tugas, UTS, dan UAS.
- Huruf mutu **tidak** disimpan di tabel `nilai`, karena akan menimbulkan ketergantungan transitif (`nilai_akhir` menentukan huruf mutu). Huruf mutu diperoleh saat query dengan mencocokkan `nilai_akhir` ke rentang di `skala_nilai`.
- Jurusan **tidak** disimpan di tabel `mahasiswa`, karena dapat diturunkan dari program studi (`mahasiswa` ke `program_studi` ke `jurusan`).
- IPS dan IPK dihitung melalui VIEW, tidak disimpan sebagai data tersendiri.

### Struktur Project

AcademicManagementSystem/
│
├── main.py
├── config.py
├── requirements.txt
├── .env.example
│
├── database/
│ ├── connection.py
│ ├── schema.sql
│ ├── seed.sql
│ ├── triggers_views.sql
│ └── create_admin.py
│
├── backend/
├── auth.py
├── user.py
├── jurusan.py
├── prodi.py
├── mahasiswa.py
├── mata_kuliah.py
├── semester.py
├── skala_nilai.py
├── nilai.py
└── ipk.py
│
├── frontend/
│ ├── main_window.py
│ ├── login_page.py
│ ├── mahasiswa_page.py
│ ├── akademik_master_page.py
│ ├── nilai_page.py
│ └── transkrip_page.py
│
├── utils/
│ ├── validators.py
│ ├── security.py
│ ├── session.py
│ └── permissions.py
│
├── docs/
│ └── erd_ipk.png
│
└── assets/
├── colors.py
└── ...

Lapisan `frontend/` tidak berisi SQL. Semua akses database dilakukan lewat `backend/`.

## Teknologi

- Python 3.10+ dengan CustomTkinter untuk GUI
- MySQL 8.0.16+ (diperlukan agar `CHECK` constraint ditegakkan)
- Library lain: lihat `requirements.txt`
- Disarankan memakai Laragon (menyediakan MySQL, HeidiSQL, dan phpMyAdmin)

## Instalasi

1. **Clone repository**

   ```bash
   git clone https://github.com/rhalstlyapp/AcademicManagementSystem.git
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

   Pastikan MySQL sudah berjalan, lalu import berurutan (jalankan di Command Prompt):

   ```bash
   mysql -u root < database\schema.sql
   mysql -u root < database\seed.sql
   mysql -u root < database\triggers_views.sql
   ```

   Perhatian: `schema.sql` menjalankan `DROP DATABASE siakad` sehingga database lama dibangun ulang dari nol.

   Operator `<` tidak didukung di PowerShell. Gunakan Command Prompt, atau perintah `source` di dalam prompt `mysql>`, atau fitur **Import** di phpMyAdmin / **Run SQL file** di HeidiSQL. Tambahkan `-p` setelah `-u root` jika MySQL kamu memakai password.

4. **Konfigurasi environment**

   ```bash
   copy .env.example .env         # Windows
   cp .env.example .env           # macOS / Linux
   ```

   Isi `DB_USER`, `DB_PASSWORD`, dan nilai lainnya di file `.env`. Pada Laragon bawaan, `DB_USER=root` dan `DB_PASSWORD` dibiarkan kosong.

5. **Buat akun admin pertama**

   ```bash
   python database/create_admin.py
   ```

   Password diketik saat skrip berjalan dan tidak tampil di layar. Mahasiswa tidak memerlukan langkah ini: mereka mendaftar sendiri lewat tombol Daftar di halaman login.

6. **Jalankan aplikasi**

   ```bash
   python main.py
   ```

   Data contoh yang bisa dipakai untuk mencoba login mahasiswa: nama `Budi Santoso` dengan NIM `2501001`.

## Alur Pengembangan

- Branch utama: `main`
- Satu branch per fitur, misalnya `feature/nilai` atau `feature/ipk`
- Pesan commit: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`

## Status

Dalam pengembangan.
