-- =====================================================================
-- schema.sql : Struktur database SIAKAD
-- DBMS       : MySQL 8.0+
--
-- Urutan menjalankan:
--   1. schema.sql
--   2. seed.sql
--   3. triggers_views.sql
--
-- PERHATIAN:
-- File ini membangun database dari nol.
-- DROP DATABASE akan menghapus database siakad beserta seluruh datanya.
-- =====================================================================


-- =====================================================================
-- 0. DATABASE
-- =====================================================================

DROP DATABASE IF EXISTS siakad;

CREATE DATABASE siakad
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE siakad;


-- =====================================================================
-- 1. ROLES
-- =====================================================================

CREATE TABLE roles (
    role_id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nama_role   VARCHAR(30) NOT NULL,

    PRIMARY KEY (role_id),
    UNIQUE KEY uq_roles_nama (nama_role)
) ENGINE=InnoDB;


-- =====================================================================
-- 2. USERS
--
-- Semua akun login berada di sini.
--
-- admin     -> profil admin
-- dosen     -> tabel dosen
-- mahasiswa -> tabel mahasiswa
--
-- Mahasiswa hasil registrasi publik dapat mempunyai:
-- password_hash = NULL
-- karena login mahasiswa memakai Nama + NIM.
--
-- foto_profil:
-- Menyimpan path relatif file foto profil.
-- File fisik disimpan di folder uploads/profile/.
-- =====================================================================

CREATE TABLE users (
    user_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
    role_id        INT UNSIGNED NOT NULL,
    username       VARCHAR(50) NOT NULL,
    email          VARCHAR(100) NULL,
    password_hash  VARCHAR(255) NULL,
    foto_profil    VARCHAR(255) NULL,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at  DATETIME NULL,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),

    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),

    KEY idx_users_role (role_id),

    CONSTRAINT fk_users_role
        FOREIGN KEY (role_id)
        REFERENCES roles (role_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 3. ADMIN
--
-- Admin mempunyai akun pada users dan profil sederhana di sini.
-- user_id juga menjadi FK ke users.
-- =====================================================================

CREATE TABLE admin (
    admin_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id        INT UNSIGNED NOT NULL,
    nama_lengkap   VARCHAR(100) NULL,

    PRIMARY KEY (admin_id),

    UNIQUE KEY uq_admin_user (user_id),

    CONSTRAINT fk_admin_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 4. JURUSAN
-- =====================================================================

CREATE TABLE jurusan (
    jurusan_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kode_jurusan  VARCHAR(10) NOT NULL,
    nama_jurusan  VARCHAR(100) NOT NULL,

    PRIMARY KEY (jurusan_id),

    UNIQUE KEY uq_jurusan_kode (kode_jurusan)
) ENGINE=InnoDB;


-- =====================================================================
-- 5. PROGRAM STUDI
-- =====================================================================

CREATE TABLE program_studi (
    prodi_id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    jurusan_id   INT UNSIGNED NOT NULL,
    kode_prodi   VARCHAR(10) NOT NULL,
    nama_prodi   VARCHAR(100) NOT NULL,
    jenjang      ENUM('D3','D4','S1','S2','S3') NOT NULL DEFAULT 'S1',

    PRIMARY KEY (prodi_id),

    UNIQUE KEY uq_prodi_kode (kode_prodi),

    KEY idx_prodi_jurusan (jurusan_id),

    CONSTRAINT fk_prodi_jurusan
        FOREIGN KEY (jurusan_id)
        REFERENCES jurusan (jurusan_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 6. DOSEN
--
-- Profil dosen terhubung ke users.
--
-- Backend dosen.py menggunakan:
--   dosen_id
--   user_id
--   prodi_id
--   nidn
--   nip
--   nama_lengkap
--   jenis_kelamin
--   status
--
-- Status:
--   Aktif
--   Cuti
--   Pensiun
--   Keluar
-- =====================================================================

CREATE TABLE dosen (
    dosen_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         INT UNSIGNED NOT NULL,
    prodi_id        INT UNSIGNED NOT NULL,

    nidn            VARCHAR(10) NULL,
    nip             VARCHAR(18) NULL,

    nama_lengkap    VARCHAR(100) NOT NULL,
    jenis_kelamin   ENUM('L','P') NOT NULL,

    status          ENUM(
        'Aktif',
        'Cuti',
        'Pensiun',
        'Keluar'
    ) NOT NULL DEFAULT 'Aktif',

    PRIMARY KEY (dosen_id),

    UNIQUE KEY uq_dosen_user (user_id),
    UNIQUE KEY uq_dosen_nidn (nidn),
    UNIQUE KEY uq_dosen_nip (nip),

    KEY idx_dosen_prodi (prodi_id),
    KEY idx_dosen_status (status),

    CONSTRAINT fk_dosen_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_dosen_prodi
        FOREIGN KEY (prodi_id)
        REFERENCES program_studi (prodi_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 7. MAHASISWA
--
-- Mahasiswa juga mempunyai akun users.
--
-- Login mahasiswa:
--   username = NIM
--   Nama + NIM
--
-- Mahasiswa mempunyai Dosen PA.
-- =====================================================================

CREATE TABLE mahasiswa (
    mahasiswa_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,

    user_id           INT UNSIGNED NOT NULL,

    prodi_id          INT UNSIGNED NOT NULL,
    dosen_pa_id       INT UNSIGNED NULL,

    nim               VARCHAR(9) NOT NULL,
    nama_lengkap      VARCHAR(100) NOT NULL,

    jenis_kelamin     ENUM('L','P') NULL,

    tempat_lahir      VARCHAR(50) NULL,
    tanggal_lahir     DATE NULL,

    agama             VARCHAR(20) NULL,
    nik               VARCHAR(16) NULL,
    alamat            TEXT NULL,
    no_hp             VARCHAR(20) NULL,

    nama_ayah         VARCHAR(100) NULL,
    nama_ibu          VARCHAR(100) NULL,

    angkatan          SMALLINT UNSIGNED NULL,

    status_mahasiswa  ENUM(
        'Aktif',
        'Cuti',
        'Lulus',
        'DO',
        'Keluar'
    ) NOT NULL DEFAULT 'Aktif',

    terdaftar_pada    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (mahasiswa_id),

    UNIQUE KEY uq_mahasiswa_user (user_id),
    UNIQUE KEY uq_mahasiswa_nim (nim),
    UNIQUE KEY uq_mahasiswa_nik (nik),

    KEY idx_mhs_prodi_angkatan (prodi_id, angkatan),
    KEY idx_mhs_nama (nama_lengkap),
    KEY idx_mhs_status (status_mahasiswa),
    KEY idx_mhs_dosen_pa (dosen_pa_id),

    CONSTRAINT fk_mhs_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_mhs_prodi
        FOREIGN KEY (prodi_id)
        REFERENCES program_studi (prodi_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_mhs_dosen_pa
        FOREIGN KEY (dosen_pa_id)
        REFERENCES dosen (dosen_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_mhs_nik
        CHECK (
            nik IS NULL
            OR (
                CHAR_LENGTH(nik) = 16
                AND nik REGEXP '^[0-9]+$'
            )
        ),

    CONSTRAINT chk_mhs_angkatan
        CHECK (
            angkatan IS NULL
            OR angkatan BETWEEN 1990 AND 2100
        )
) ENGINE=InnoDB;


-- =====================================================================
-- 8. KURIKULUM
--
-- Setiap program studi dapat mempunyai beberapa kurikulum.
--
-- Contoh:
--   TI 2025
--   TI 2026
-- =====================================================================

CREATE TABLE kurikulum (
    kurikulum_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    prodi_id        INT UNSIGNED NOT NULL,

    nama_kurikulum  VARCHAR(100) NOT NULL,
    tahun_berlaku   SMALLINT UNSIGNED NOT NULL,

    is_aktif        BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (kurikulum_id),

    UNIQUE KEY uq_kurikulum_prodi_tahun
        (prodi_id, tahun_berlaku),

    KEY idx_kurikulum_prodi (prodi_id),

    CONSTRAINT fk_kurikulum_prodi
        FOREIGN KEY (prodi_id)
        REFERENCES program_studi (prodi_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_kurikulum_tahun
        CHECK (tahun_berlaku BETWEEN 1990 AND 2100)
) ENGINE=InnoDB;


-- =====================================================================
-- 9. MATA KULIAH
-- =====================================================================

CREATE TABLE mata_kuliah (
    mk_id           INT UNSIGNED NOT NULL AUTO_INCREMENT,

    kurikulum_id    INT UNSIGNED NOT NULL,

    kode_mk         VARCHAR(15) NOT NULL,
    nama_mk         VARCHAR(150) NOT NULL,

    sks             TINYINT UNSIGNED NOT NULL,

    semester_paket  TINYINT UNSIGNED NOT NULL,

    jenis_mk        ENUM('Wajib','Pilihan') NOT NULL DEFAULT 'Wajib',

    PRIMARY KEY (mk_id),

    UNIQUE KEY uq_mk_kode (kode_mk),

    KEY idx_mk_kurikulum (kurikulum_id),
    KEY idx_mk_nama (nama_mk),

    CONSTRAINT fk_mk_kurikulum
        FOREIGN KEY (kurikulum_id)
        REFERENCES kurikulum (kurikulum_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_mk_sks
        CHECK (sks BETWEEN 1 AND 6),

    CONSTRAINT chk_mk_semester
        CHECK (semester_paket BETWEEN 1 AND 8)
) ENGINE=InnoDB;


-- =====================================================================
-- 10. PRASYARAT MATA KULIAH
--
-- Contoh:
--   Basis Data II membutuhkan Basis Data I.
-- =====================================================================

CREATE TABLE prasyarat_mk (
    mk_id           INT UNSIGNED NOT NULL,
    mk_prasyarat_id INT UNSIGNED NOT NULL,

    PRIMARY KEY (mk_id, mk_prasyarat_id),

    CONSTRAINT fk_prasyarat_mk_mk
        FOREIGN KEY (mk_id)
        REFERENCES mata_kuliah(mk_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_prasyarat_mk_prasyarat
        FOREIGN KEY (mk_prasyarat_id)
        REFERENCES mata_kuliah(mk_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- =====================================================================
-- 11. SEMESTER AKADEMIK
-- =====================================================================

CREATE TABLE semester_akademik (
    semester_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,

    kode_semester     CHAR(5) NOT NULL,

    tahun_akademik    VARCHAR(9) NOT NULL,

    jenis             ENUM(
        'Ganjil',
        'Genap',
        'Pendek'
    ) NOT NULL,

    tgl_mulai         DATE NOT NULL,
    tgl_selesai       DATE NOT NULL,

    tgl_mulai_krs     DATE NOT NULL,
    tgl_selesai_krs   DATE NOT NULL,

    is_aktif          BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (semester_id),

    UNIQUE KEY uq_semester_kode (kode_semester),

    KEY idx_semester_aktif (is_aktif),

    CONSTRAINT chk_semester_kode
        CHECK (
            kode_semester REGEXP '^[0-9]{4}[123]$'
        ),

    CONSTRAINT chk_semester_tanggal
        CHECK (tgl_selesai > tgl_mulai),

    CONSTRAINT chk_semester_krs
        CHECK (tgl_selesai_krs >= tgl_mulai_krs)
) ENGINE=InnoDB;


-- =====================================================================
-- 12. KELAS
--
-- Kelas tidak menyimpan dosen_id langsung.
--
-- Relasi dosen dilakukan melalui:
--
--   kelas
--      ↓
--   kelas_dosen
--      ↓
--   dosen
--
-- Ini memungkinkan satu kelas memiliki lebih dari satu dosen.
-- =====================================================================

CREATE TABLE kelas (
    kelas_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,

    mk_id          INT UNSIGNED NOT NULL,
    semester_id    INT UNSIGNED NOT NULL,

    nama_kelas     VARCHAR(20) NOT NULL,
    kuota          SMALLINT UNSIGNED NOT NULL,

    PRIMARY KEY (kelas_id),

    UNIQUE KEY uq_kelas_mk_semester_nama
        (mk_id, semester_id, nama_kelas),

    KEY idx_kelas_semester (semester_id),
    KEY idx_kelas_mk (mk_id),

    CONSTRAINT fk_kelas_mk
        FOREIGN KEY (mk_id)
        REFERENCES mata_kuliah (mk_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_kelas_semester
        FOREIGN KEY (semester_id)
        REFERENCES semester_akademik (semester_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_kelas_kuota
        CHECK (kuota BETWEEN 1 AND 65535)
) ENGINE=InnoDB;


-- =====================================================================
-- 13. KELAS_DOSEN
--
-- Hubungan:
--
--   satu kelas  -> bisa beberapa dosen
--   satu dosen  -> bisa mengajar beberapa kelas
--
-- Peran:
--   Koordinator
--   Pengajar
-- =====================================================================

CREATE TABLE kelas_dosen (
    kelas_id      INT UNSIGNED NOT NULL,
    dosen_id      INT UNSIGNED NOT NULL,

    peran         ENUM(
        'Koordinator',
        'Pengajar'
    ) NOT NULL DEFAULT 'Pengajar',

    PRIMARY KEY (kelas_id, dosen_id),

    KEY idx_kelas_dosen_dosen (dosen_id),

    CONSTRAINT fk_kelas_dosen_kelas
        FOREIGN KEY (kelas_id)
        REFERENCES kelas (kelas_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_kelas_dosen_dosen
        FOREIGN KEY (dosen_id)
        REFERENCES dosen (dosen_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 14. KRS
--
-- Mahasiswa memilih kelas pada suatu semester.
-- =====================================================================

CREATE TABLE krs (
    krs_id          INT UNSIGNED NOT NULL AUTO_INCREMENT,

    mahasiswa_id    INT UNSIGNED NOT NULL,
    semester_id     INT UNSIGNED NOT NULL,

    status          ENUM(
        'Draft',
        'Diajukan',
        'Disetujui',
        'Ditolak'
    ) NOT NULL DEFAULT 'Draft',

    tanggal_pengajuan   DATETIME NULL,
    tanggal_persetujuan DATETIME NULL,

    PRIMARY KEY (krs_id),

    UNIQUE KEY uq_krs_mahasiswa_semester
        (mahasiswa_id, semester_id),

    KEY idx_krs_semester (semester_id),
    KEY idx_krs_status (status),

    CONSTRAINT fk_krs_mahasiswa
        FOREIGN KEY (mahasiswa_id)
        REFERENCES mahasiswa (mahasiswa_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_krs_semester
        FOREIGN KEY (semester_id)
        REFERENCES semester_akademik (semester_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 15. KRS DETAIL
--
-- Satu baris = satu mata kuliah/kelas yang diambil mahasiswa.
-- =====================================================================

CREATE TABLE krs_detail (
    krs_detail_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,

    krs_id          INT UNSIGNED NOT NULL,
    kelas_id        INT UNSIGNED NOT NULL,

    PRIMARY KEY (krs_detail_id),

    UNIQUE KEY uq_krs_detail_kelas
        (krs_id, kelas_id),

    KEY idx_krs_detail_kelas (kelas_id),

    CONSTRAINT fk_krs_detail_krs
        FOREIGN KEY (krs_id)
        REFERENCES krs (krs_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_krs_detail_kelas
        FOREIGN KEY (kelas_id)
        REFERENCES kelas (kelas_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;


-- =====================================================================
-- 16. SKALA NILAI
--
-- Rentang:
--
-- A   = 85 - 100
-- AB  = 80 - 84.99
-- B   = 70 - 79.99
-- BC  = 65 - 69.99
-- C   = 55 - 64.99
-- D   = 40 - 54.99
-- E   = 0  - 39.99
-- =====================================================================

CREATE TABLE skala_nilai (
    skala_id     SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,

    huruf_mutu   CHAR(2) NOT NULL,
    bobot_mutu   DECIMAL(3,2) NOT NULL,

    nilai_min    DECIMAL(5,2) NOT NULL,
    nilai_max    DECIMAL(5,2) NOT NULL,

    is_lulus     BOOLEAN NOT NULL,

    PRIMARY KEY (skala_id),

    UNIQUE KEY uq_skala_huruf (huruf_mutu),

    CONSTRAINT chk_skala_bobot
        CHECK (bobot_mutu BETWEEN 0 AND 4),

    CONSTRAINT chk_skala_rentang
        CHECK (
            nilai_min >= 0
            AND nilai_min <= nilai_max
            AND nilai_max <= 100
        )
) ENGINE=InnoDB;


-- =====================================================================
-- 17. NILAI_AKHIR
--
-- Nilai final yang berasal dari KRS.
--
-- Nilai diinput oleh dosen.
-- =====================================================================

CREATE TABLE nilai_akhir (
    nilai_akhir_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,

    krs_detail_id    INT UNSIGNED NOT NULL,

    nilai_angka      DECIMAL(5,2) NOT NULL,

    skala_id         SMALLINT UNSIGNED NOT NULL,

    is_final         BOOLEAN NOT NULL DEFAULT FALSE,

    diinput_oleh     INT UNSIGNED NULL,

    finalized_at     DATETIME NULL,

    PRIMARY KEY (nilai_akhir_id),

    UNIQUE KEY uq_nilai_akhir_krs_detail
        (krs_detail_id),

    KEY idx_nilai_akhir_skala (skala_id),
    KEY idx_nilai_akhir_dosen (diinput_oleh),

    CONSTRAINT fk_nilai_akhir_krs_detail
        FOREIGN KEY (krs_detail_id)
        REFERENCES krs_detail (krs_detail_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_nilai_akhir_skala
        FOREIGN KEY (skala_id)
        REFERENCES skala_nilai (skala_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_nilai_akhir_dosen
        FOREIGN KEY (diinput_oleh)
        REFERENCES dosen (dosen_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_nilai_akhir_rentang
        CHECK (nilai_angka BETWEEN 0 AND 100)
) ENGINE=InnoDB;


-- =====================================================================
-- 18. NILAI MAHASISWA
--
-- Tabel ini dipakai langsung oleh backend/nilai.py.
--
-- UNIQUE:
--   mahasiswa + mata kuliah + semester
--
-- Artinya satu mahasiswa tidak mempunyai dua nilai final
-- untuk mata kuliah yang sama pada semester yang sama.
--
-- Tabel ini juga memungkinkan sistem menghitung:
--   - transkrip
--   - IPS
--   - IPK
-- =====================================================================

CREATE TABLE nilai_mahasiswa (
    nilai_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,

    mahasiswa_id    INT UNSIGNED NOT NULL,
    mk_id           INT UNSIGNED NOT NULL,
    semester_id     INT UNSIGNED NOT NULL,

    nilai_angka     DECIMAL(5,2) NOT NULL,
    skala_id        SMALLINT UNSIGNED NOT NULL,

    is_final        BOOLEAN NOT NULL DEFAULT TRUE,

    diinput_oleh    INT UNSIGNED NULL,
    finalized_at    DATETIME NULL,

    PRIMARY KEY (nilai_id),

    UNIQUE KEY uq_nilai_mhs_mk_semester
        (mahasiswa_id, mk_id, semester_id),

    KEY idx_nilai_mhs_semester (semester_id),
    KEY idx_nilai_mhs_mk (mk_id),
    KEY idx_nilai_mhs_dosen (diinput_oleh),

    CONSTRAINT fk_nm_mahasiswa
        FOREIGN KEY (mahasiswa_id)
        REFERENCES mahasiswa (mahasiswa_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_nm_mk
        FOREIGN KEY (mk_id)
        REFERENCES mata_kuliah (mk_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_nm_semester
        FOREIGN KEY (semester_id)
        REFERENCES semester_akademik (semester_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_nm_skala
        FOREIGN KEY (skala_id)
        REFERENCES skala_nilai (skala_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_nm_dosen
        FOREIGN KEY (diinput_oleh)
        REFERENCES dosen (dosen_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_nilai_mahasiswa_rentang
        CHECK (nilai_angka BETWEEN 0 AND 100)
) ENGINE=InnoDB;


-- =====================================================================
-- 19. IP SEMESTER
--
-- Menyimpan hasil perhitungan IPS jika nanti digunakan oleh backend.
-- =====================================================================

CREATE TABLE ip_semester (
    ip_semester_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,

    mahasiswa_id     INT UNSIGNED NOT NULL,
    semester_id      INT UNSIGNED NOT NULL,

    total_sks        DECIMAL(5,2) NOT NULL DEFAULT 0,
    total_sks_lulus  DECIMAL(5,2) NOT NULL DEFAULT 0,
    total_mutu       DECIMAL(7,2) NOT NULL DEFAULT 0,

    ips              DECIMAL(4,2) NULL,

    PRIMARY KEY (ip_semester_id),

    UNIQUE KEY uq_ip_semester_mhs_semester
        (mahasiswa_id, semester_id),

    CONSTRAINT fk_ip_semester_mahasiswa
        FOREIGN KEY (mahasiswa_id)
        REFERENCES mahasiswa (mahasiswa_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_ip_semester_semester
        FOREIGN KEY (semester_id)
        REFERENCES semester_akademik (semester_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_ips
        CHECK (
            ips IS NULL
            OR ips BETWEEN 0 AND 4
        )
) ENGINE=InnoDB;


-- =====================================================================
-- 20. TUGAS MAHASISWA
--
-- Menyimpan daftar tugas pribadi mahasiswa.
--
-- Backend:
--   backend/tugas.py
--
-- Satu tugas hanya dimiliki oleh satu mahasiswa.
-- =====================================================================

CREATE TABLE tugas_mahasiswa (
    tugas_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,

    mahasiswa_id    INT UNSIGNED NOT NULL,

    judul           VARCHAR(255) NOT NULL,
    catatan         TEXT NULL,

    tanggal         DATE NOT NULL,

    selesai         BOOLEAN NOT NULL DEFAULT FALSE,

    dibuat_pada     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    diubah_pada     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (tugas_id),

    KEY idx_tugas_mahasiswa (mahasiswa_id),
    KEY idx_tugas_tanggal (tanggal),
    KEY idx_tugas_selesai (selesai),

    CONSTRAINT fk_tugas_mahasiswa_mahasiswa
        FOREIGN KEY (mahasiswa_id)
        REFERENCES mahasiswa (mahasiswa_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================================
-- 21. PENGAJUAN PERUBAHAN NIM
--
-- Mahasiswa tidak mengubah NIM secara langsung.
-- Mahasiswa mengirim pengajuan kepada admin.
--
-- Alur:
--   Menunggu -> Disetujui / Ditolak
--
-- Jika disetujui:
--   mahasiswa.nim  -> NIM baru
--   users.username  -> NIM baru
--
-- Keduanya harus berubah dalam satu transaksi.
-- =====================================================================

CREATE TABLE pengajuan_perubahan_nim (
    pengajuan_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,

    mahasiswa_id        INT UNSIGNED NOT NULL,

    nim_lama            VARCHAR(9) NOT NULL,
    nim_baru            VARCHAR(9) NOT NULL,

    alasan              VARCHAR(255) NOT NULL,

    status              ENUM(
        'Menunggu',
        'Disetujui',
        'Ditolak'
    ) NOT NULL DEFAULT 'Menunggu',

    diproses_oleh       INT UNSIGNED NULL,

    catatan_admin       VARCHAR(255) NULL,

    tanggal_pengajuan   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tanggal_diproses    DATETIME NULL,

    PRIMARY KEY (pengajuan_id),

    KEY idx_pengajuan_mahasiswa (mahasiswa_id),
    KEY idx_pengajuan_status (status),
    KEY idx_pengajuan_admin (diproses_oleh),

    CONSTRAINT fk_pengajuan_mahasiswa
        FOREIGN KEY (mahasiswa_id)
        REFERENCES mahasiswa (mahasiswa_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_pengajuan_admin
        FOREIGN KEY (diproses_oleh)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_nim_baru_9_digit
        CHECK (
            CHAR_LENGTH(nim_baru) = 9
            AND nim_baru REGEXP '^[0-9]{9}$'
        ),

    CONSTRAINT chk_nim_lama_9_digit
        CHECK (
            CHAR_LENGTH(nim_lama) = 9
            AND nim_lama REGEXP '^[0-9]{9}$'
        ),

    CONSTRAINT chk_nim_tidak_sama
        CHECK (
            nim_lama <> nim_baru
        )
) ENGINE=InnoDB;

CONSTRAINT chk_mhs_nim_9_digit
    CHECK (
        CHAR_LENGTH(nim) = 9
        AND nim REGEXP '^[0-9]{9}$'
    ),

-- =====================================================================
-- SELESAI
-- =====================================================================

SELECT 'Schema SIAKAD berhasil dibuat.' AS status;
