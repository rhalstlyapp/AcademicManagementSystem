-- =====================================================================
-- schema.sql : Struktur database SIAKAD (AcademicManagementSystem)
-- DBMS       : MySQL 8.0.16+ (CHECK constraint hanya ditegakkan mulai versi ini)
-- Normalisasi: 3NF
-- Urutan     : tabel induk dibuat lebih dulu daripada tabel yang mereferensikannya
-- =====================================================================

CREATE DATABASE IF NOT EXISTS siakad
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE siakad;

-- =====================================================================
-- A. USER & ROLE
-- =====================================================================

CREATE TABLE IF NOT EXISTS roles (
    role_id    SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nama_role  VARCHAR(20)       NOT NULL,
    PRIMARY KEY (role_id),
    UNIQUE KEY uq_roles_nama (nama_role)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    user_id        INT UNSIGNED      NOT NULL AUTO_INCREMENT,
    role_id        SMALLINT UNSIGNED NOT NULL,
    username       VARCHAR(50)       NOT NULL,   -- NIM / NIDN / username admin
    email          VARCHAR(100)      NOT NULL,
    password_hash  VARCHAR(255)      NOT NULL,   -- bcrypt / argon2, JANGAN simpan password asli
    is_active      BOOLEAN           NOT NULL DEFAULT TRUE,
    last_login_at  DATETIME          NULL,
    created_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_role (role_id),
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles (role_id)
) ENGINE=InnoDB;

-- =====================================================================
-- B. MASTER AKADEMIK
-- =====================================================================

CREATE TABLE IF NOT EXISTS fakultas (
    fakultas_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kode_fakultas  VARCHAR(10)  NOT NULL,
    nama_fakultas  VARCHAR(100) NOT NULL,
    PRIMARY KEY (fakultas_id),
    UNIQUE KEY uq_fakultas_kode (kode_fakultas)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS program_studi (
    prodi_id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    fakultas_id  INT UNSIGNED NOT NULL,
    kode_prodi   VARCHAR(10)  NOT NULL,
    nama_prodi   VARCHAR(100) NOT NULL,
    jenjang      ENUM('D3','D4','S1','S2','S3') NOT NULL,
    PRIMARY KEY (prodi_id),
    UNIQUE KEY uq_prodi_kode (kode_prodi),
    KEY idx_prodi_fakultas (fakultas_id),
    CONSTRAINT fk_prodi_fakultas FOREIGN KEY (fakultas_id) REFERENCES fakultas (fakultas_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS semester_akademik (
    semester_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kode_semester     CHAR(5)      NOT NULL,                 -- contoh: 20261 (tahun + 1 ganjil / 2 genap / 3 pendek)
    tahun_akademik    VARCHAR(9)   NOT NULL,                 -- contoh: 2026/2027
    jenis             ENUM('Ganjil','Genap','Pendek') NOT NULL,
    tgl_mulai         DATE         NOT NULL,
    tgl_selesai       DATE         NOT NULL,
    tgl_mulai_krs     DATE         NOT NULL,
    tgl_selesai_krs   DATE         NOT NULL,
    is_aktif          BOOLEAN      NOT NULL DEFAULT FALSE,
    -- Kolom bantu agar hanya SATU semester yang boleh aktif.
    -- Bernilai 1 saat aktif, NULL saat tidak; UNIQUE mengizinkan banyak NULL.
    aktif_flag        TINYINT GENERATED ALWAYS AS (IF(is_aktif, 1, NULL)) STORED,
    PRIMARY KEY (semester_id),
    UNIQUE KEY uq_semester_kode (kode_semester),
    UNIQUE KEY uq_semester_hanya_satu_aktif (aktif_flag),
    CONSTRAINT chk_semester_tanggal CHECK (tgl_selesai > tgl_mulai),
    CONSTRAINT chk_semester_krs     CHECK (tgl_selesai_krs >= tgl_mulai_krs)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ruang (
    ruang_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kode_ruang  VARCHAR(15)  NOT NULL,
    nama_ruang  VARCHAR(50)  NOT NULL,
    gedung      VARCHAR(50)  NULL,
    kapasitas   SMALLINT UNSIGNED NOT NULL,
    jenis       ENUM('Kelas','Lab','Aula') NOT NULL DEFAULT 'Kelas',
    PRIMARY KEY (ruang_id),
    UNIQUE KEY uq_ruang_kode (kode_ruang),
    CONSTRAINT chk_ruang_kapasitas CHECK (kapasitas > 0)
) ENGINE=InnoDB;

-- =====================================================================
-- C. DOSEN & MAHASISWA
-- =====================================================================

CREATE TABLE IF NOT EXISTS dosen (
    dosen_id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id             INT UNSIGNED NOT NULL,
    prodi_id            INT UNSIGNED NOT NULL,           -- homebase
    nidn                VARCHAR(10)  NULL,
    nip                 VARCHAR(18)  NULL,
    nama_lengkap        VARCHAR(100) NOT NULL,
    gelar_depan         VARCHAR(30)  NULL,
    gelar_belakang      VARCHAR(30)  NULL,
    jenis_kelamin       ENUM('L','P') NOT NULL,
    tempat_lahir        VARCHAR(50)  NULL,
    tanggal_lahir       DATE         NULL,
    no_hp               VARCHAR(20)  NULL,
    alamat              TEXT         NULL,
    jabatan_fungsional  VARCHAR(30)  NULL,
    status              ENUM('Aktif','Cuti','Pensiun','Keluar') NOT NULL DEFAULT 'Aktif',
    PRIMARY KEY (dosen_id),
    UNIQUE KEY uq_dosen_user (user_id),
    UNIQUE KEY uq_dosen_nidn (nidn),
    UNIQUE KEY uq_dosen_nip (nip),
    KEY idx_dosen_prodi (prodi_id),
    KEY idx_dosen_nama (nama_lengkap),
    CONSTRAINT fk_dosen_user  FOREIGN KEY (user_id)  REFERENCES users (user_id),
    CONSTRAINT fk_dosen_prodi FOREIGN KEY (prodi_id) REFERENCES program_studi (prodi_id),
    CONSTRAINT chk_dosen_identitas CHECK (nidn IS NOT NULL OR nip IS NOT NULL)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mahasiswa (
    mahasiswa_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id           INT UNSIGNED NOT NULL,
    prodi_id          INT UNSIGNED NOT NULL,
    dosen_pa_id       INT UNSIGNED NOT NULL,              -- Dosen Wali / PA
    nim               VARCHAR(15)  NOT NULL,
    nama_lengkap      VARCHAR(100) NOT NULL,
    jenis_kelamin     ENUM('L','P') NOT NULL,
    tempat_lahir      VARCHAR(50)  NULL,
    tanggal_lahir     DATE         NOT NULL,
    agama             VARCHAR(20)  NULL,
    nik               CHAR(16)     NULL,
    alamat            TEXT         NULL,
    no_hp             VARCHAR(20)  NULL,
    nama_ayah         VARCHAR(100) NULL,
    nama_ibu          VARCHAR(100) NULL,
    angkatan          SMALLINT UNSIGNED NOT NULL,
    status_mahasiswa  ENUM('Aktif','Cuti','Lulus','DO','Keluar') NOT NULL DEFAULT 'Aktif',
    PRIMARY KEY (mahasiswa_id),
    UNIQUE KEY uq_mahasiswa_user (user_id),
    UNIQUE KEY uq_mahasiswa_nim (nim),
    UNIQUE KEY uq_mahasiswa_nik (nik),
    KEY idx_mhs_prodi_angkatan_status (prodi_id, angkatan, status_mahasiswa),
    KEY idx_mhs_dosen_pa (dosen_pa_id),
    KEY idx_mhs_nama (nama_lengkap),
    KEY idx_mhs_status (status_mahasiswa),
    CONSTRAINT fk_mhs_user  FOREIGN KEY (user_id)     REFERENCES users (user_id),
    CONSTRAINT fk_mhs_prodi FOREIGN KEY (prodi_id)    REFERENCES program_studi (prodi_id),
    CONSTRAINT fk_mhs_pa    FOREIGN KEY (dosen_pa_id) REFERENCES dosen (dosen_id),
    CONSTRAINT chk_mhs_angkatan CHECK (angkatan BETWEEN 1990 AND 2100)
) ENGINE=InnoDB;

-- =====================================================================
-- D. KURIKULUM & MATA KULIAH
-- =====================================================================

CREATE TABLE IF NOT EXISTS kurikulum (
    kurikulum_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    prodi_id        INT UNSIGNED NOT NULL,
    nama_kurikulum  VARCHAR(100) NOT NULL,
    tahun_berlaku   SMALLINT UNSIGNED NOT NULL,
    is_aktif        BOOLEAN      NOT NULL DEFAULT TRUE,
    PRIMARY KEY (kurikulum_id),
    UNIQUE KEY uq_kurikulum_prodi_nama (prodi_id, nama_kurikulum),
    CONSTRAINT fk_kurikulum_prodi FOREIGN KEY (prodi_id) REFERENCES program_studi (prodi_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mata_kuliah (
    mk_id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kurikulum_id    INT UNSIGNED NOT NULL,
    kode_mk         VARCHAR(15)  NOT NULL,
    nama_mk         VARCHAR(150) NOT NULL,
    sks             TINYINT UNSIGNED NOT NULL,
    semester_paket  TINYINT UNSIGNED NOT NULL,
    jenis_mk        ENUM('Wajib','Pilihan') NOT NULL DEFAULT 'Wajib',
    PRIMARY KEY (mk_id),
    UNIQUE KEY uq_mk_kode (kode_mk),
    KEY idx_mk_kurikulum_semester (kurikulum_id, semester_paket),
    KEY idx_mk_nama (nama_mk),
    CONSTRAINT fk_mk_kurikulum FOREIGN KEY (kurikulum_id) REFERENCES kurikulum (kurikulum_id),
    CONSTRAINT chk_mk_sks      CHECK (sks BETWEEN 1 AND 6),
    CONSTRAINT chk_mk_semester CHECK (semester_paket BETWEEN 1 AND 8)
) ENGINE=InnoDB;

-- =====================================================================
-- E. NILAI REFERENSI (dibuat sebelum prasyarat_mk karena direferensikan)
-- =====================================================================

CREATE TABLE IF NOT EXISTS skala_nilai (
    skala_id    SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    huruf_mutu  CHAR(2)       NOT NULL,                   -- A, AB, B, BC, C, D, E
    bobot_mutu  DECIMAL(3,2)  NOT NULL,                   -- 4.00 ... 0.00
    nilai_min   DECIMAL(5,2)  NOT NULL,
    nilai_max   DECIMAL(5,2)  NOT NULL,
    is_lulus    BOOLEAN       NOT NULL,
    PRIMARY KEY (skala_id),
    UNIQUE KEY uq_skala_huruf (huruf_mutu),
    CONSTRAINT chk_skala_rentang CHECK (nilai_min >= 0 AND nilai_min <= nilai_max AND nilai_max <= 100),
    CONSTRAINT chk_skala_bobot   CHECK (bobot_mutu BETWEEN 0 AND 4)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS prasyarat_mk (
    mk_id            INT UNSIGNED      NOT NULL,
    mk_prasyarat_id  INT UNSIGNED      NOT NULL,
    skala_id         SMALLINT UNSIGNED NULL,              -- nilai minimal yang disyaratkan
    PRIMARY KEY (mk_id, mk_prasyarat_id),
    KEY idx_prasyarat_mk_syarat (mk_prasyarat_id),
    CONSTRAINT fk_prasyarat_mk     FOREIGN KEY (mk_id)           REFERENCES mata_kuliah (mk_id),
    CONSTRAINT fk_prasyarat_syarat FOREIGN KEY (mk_prasyarat_id) REFERENCES mata_kuliah (mk_id),
    CONSTRAINT fk_prasyarat_skala  FOREIGN KEY (skala_id)        REFERENCES skala_nilai (skala_id),
    CONSTRAINT chk_prasyarat_beda  CHECK (mk_id <> mk_prasyarat_id)
) ENGINE=InnoDB;

-- =====================================================================
-- F. KELAS & JADWAL
-- =====================================================================

CREATE TABLE IF NOT EXISTS kelas (
    kelas_id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
    mk_id        INT UNSIGNED NOT NULL,
    semester_id  INT UNSIGNED NOT NULL,
    nama_kelas   VARCHAR(5)   NOT NULL,                   -- A, B, C
    kuota        SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (kelas_id),
    UNIQUE KEY uq_kelas_mk_semester_nama (mk_id, semester_id, nama_kelas),
    KEY idx_kelas_semester_mk (semester_id, mk_id),
    CONSTRAINT fk_kelas_mk       FOREIGN KEY (mk_id)       REFERENCES mata_kuliah (mk_id),
    CONSTRAINT fk_kelas_semester FOREIGN KEY (semester_id) REFERENCES semester_akademik (semester_id),
    CONSTRAINT chk_kelas_kuota   CHECK (kuota > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS kelas_dosen (
    kelas_id  INT UNSIGNED NOT NULL,
    dosen_id  INT UNSIGNED NOT NULL,
    peran     ENUM('Koordinator','Anggota') NOT NULL DEFAULT 'Koordinator',
    PRIMARY KEY (kelas_id, dosen_id),
    KEY idx_kelas_dosen_dosen (dosen_id),
    CONSTRAINT fk_kd_kelas FOREIGN KEY (kelas_id) REFERENCES kelas (kelas_id) ON DELETE CASCADE,
    CONSTRAINT fk_kd_dosen FOREIGN KEY (dosen_id) REFERENCES dosen (dosen_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jadwal_kelas (
    jadwal_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kelas_id     INT UNSIGNED NOT NULL,
    ruang_id     INT UNSIGNED NOT NULL,
    hari         TINYINT UNSIGNED NOT NULL,               -- 1 = Senin ... 7 = Minggu
    jam_mulai    TIME NOT NULL,
    jam_selesai  TIME NOT NULL,
    PRIMARY KEY (jadwal_id),
    UNIQUE KEY uq_jadwal_kelas_hari_jam (kelas_id, hari, jam_mulai),
    KEY idx_jadwal_ruang_waktu (ruang_id, hari, jam_mulai, jam_selesai),
    CONSTRAINT fk_jadwal_kelas FOREIGN KEY (kelas_id) REFERENCES kelas (kelas_id) ON DELETE CASCADE,
    CONSTRAINT fk_jadwal_ruang FOREIGN KEY (ruang_id) REFERENCES ruang (ruang_id),
    CONSTRAINT chk_jadwal_hari CHECK (hari BETWEEN 1 AND 7),
    CONSTRAINT chk_jadwal_jam  CHECK (jam_selesai > jam_mulai)
) ENGINE=InnoDB;

-- =====================================================================
-- G. KRS
-- =====================================================================

CREATE TABLE IF NOT EXISTS aturan_batas_sks (
    aturan_id  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ips_min    DECIMAL(3,2) NOT NULL,
    ips_max    DECIMAL(3,2) NOT NULL,
    sks_maks   TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (aturan_id),
    CONSTRAINT chk_aturan_ips CHECK (ips_min >= 0 AND ips_min <= ips_max AND ips_max <= 4),
    CONSTRAINT chk_aturan_sks CHECK (sks_maks > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS krs (
    krs_id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
    mahasiswa_id     INT UNSIGNED NOT NULL,
    semester_id      INT UNSIGNED NOT NULL,
    status           ENUM('Draft','Diajukan','Disetujui','Ditolak') NOT NULL DEFAULT 'Draft',
    tgl_pengajuan    DATETIME     NULL,
    disetujui_oleh   INT UNSIGNED NULL,                   -- dosen PA
    tgl_persetujuan  DATETIME     NULL,
    catatan_pa       VARCHAR(255) NULL,
    PRIMARY KEY (krs_id),
    UNIQUE KEY uq_krs_mhs_semester (mahasiswa_id, semester_id),
    KEY idx_krs_semester_status (semester_id, status),
    KEY idx_krs_disetujui_oleh (disetujui_oleh),
    CONSTRAINT fk_krs_mhs      FOREIGN KEY (mahasiswa_id)   REFERENCES mahasiswa (mahasiswa_id),
    CONSTRAINT fk_krs_semester FOREIGN KEY (semester_id)    REFERENCES semester_akademik (semester_id),
    CONSTRAINT fk_krs_dosen    FOREIGN KEY (disetujui_oleh) REFERENCES dosen (dosen_id),
    CONSTRAINT chk_krs_approval CHECK (status NOT IN ('Disetujui','Ditolak') OR disetujui_oleh IS NOT NULL)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS krs_detail (
    krs_detail_id  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    krs_id         INT UNSIGNED NOT NULL,
    kelas_id       INT UNSIGNED NOT NULL,
    status_ambil   ENUM('Baru','Mengulang','Perbaikan') NOT NULL DEFAULT 'Baru',
    PRIMARY KEY (krs_detail_id),
    UNIQUE KEY uq_krs_detail (krs_id, kelas_id),
    KEY idx_krs_detail_kelas (kelas_id),
    CONSTRAINT fk_kd_krs   FOREIGN KEY (krs_id)   REFERENCES krs (krs_id) ON DELETE CASCADE,
    CONSTRAINT fk_krsd_kelas FOREIGN KEY (kelas_id) REFERENCES kelas (kelas_id)
) ENGINE=InnoDB;

-- =====================================================================
-- H. NILAI
-- =====================================================================

CREATE TABLE IF NOT EXISTS komponen_nilai (
    komponen_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kelas_id       INT UNSIGNED NOT NULL,
    nama_komponen  VARCHAR(30)  NOT NULL,                 -- Tugas, UTS, UAS, Kehadiran
    bobot_persen   DECIMAL(5,2) NOT NULL,
    PRIMARY KEY (komponen_id),
    UNIQUE KEY uq_komponen_kelas_nama (kelas_id, nama_komponen),
    CONSTRAINT fk_komponen_kelas FOREIGN KEY (kelas_id) REFERENCES kelas (kelas_id) ON DELETE CASCADE,
    CONSTRAINT chk_komponen_bobot CHECK (bobot_persen BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nilai_komponen (
    nilai_komponen_id  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    krs_detail_id      INT UNSIGNED    NOT NULL,
    komponen_id        INT UNSIGNED    NOT NULL,
    nilai              DECIMAL(5,2)    NOT NULL,
    PRIMARY KEY (nilai_komponen_id),
    UNIQUE KEY uq_nilai_komponen (krs_detail_id, komponen_id),
    KEY idx_nilai_komponen_komponen (komponen_id),
    CONSTRAINT fk_nk_krsd     FOREIGN KEY (krs_detail_id) REFERENCES krs_detail (krs_detail_id) ON DELETE CASCADE,
    CONSTRAINT fk_nk_komponen FOREIGN KEY (komponen_id)   REFERENCES komponen_nilai (komponen_id),
    CONSTRAINT chk_nk_nilai   CHECK (nilai BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS nilai_akhir (
    krs_detail_id  INT UNSIGNED      NOT NULL,            -- 1:1 dengan krs_detail
    skala_id       SMALLINT UNSIGNED NULL,                -- NULL sebelum finalisasi
    nilai_angka    DECIMAL(5,2)      NULL,
    is_final       BOOLEAN           NOT NULL DEFAULT FALSE,
    diinput_oleh   INT UNSIGNED      NOT NULL,            -- dosen
    finalized_at   DATETIME          NULL,
    PRIMARY KEY (krs_detail_id),
    KEY idx_na_skala (skala_id),
    KEY idx_na_dosen (diinput_oleh),
    CONSTRAINT fk_na_krsd   FOREIGN KEY (krs_detail_id) REFERENCES krs_detail (krs_detail_id) ON DELETE CASCADE,
    CONSTRAINT fk_na_skala  FOREIGN KEY (skala_id)      REFERENCES skala_nilai (skala_id),
    CONSTRAINT fk_na_dosen  FOREIGN KEY (diinput_oleh)  REFERENCES dosen (dosen_id),
    CONSTRAINT chk_na_angka CHECK (nilai_angka IS NULL OR nilai_angka BETWEEN 0 AND 100),
    CONSTRAINT chk_na_final CHECK (is_final = FALSE OR (skala_id IS NOT NULL AND nilai_angka IS NOT NULL))
) ENGINE=InnoDB;

-- =====================================================================
-- I. IP SEMESTER / IPK (snapshot hasil perhitungan)
-- =====================================================================

CREATE TABLE IF NOT EXISTS ip_semester (
    ip_id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    mahasiswa_id   INT UNSIGNED NOT NULL,
    semester_id    INT UNSIGNED NOT NULL,
    sks_diambil    SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    sks_lulus      SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    total_mutu     DECIMAL(7,2) NOT NULL DEFAULT 0,       -- sigma (SKS x bobot_mutu)
    ips            DECIMAL(3,2) NOT NULL DEFAULT 0,
    sks_kumulatif  SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    ipk            DECIMAL(3,2) NOT NULL DEFAULT 0,
    calculated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ip_id),
    UNIQUE KEY uq_ip_mhs_semester (mahasiswa_id, semester_id),
    KEY idx_ip_semester (semester_id),
    CONSTRAINT fk_ip_mhs      FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa (mahasiswa_id),
    CONSTRAINT fk_ip_semester FOREIGN KEY (semester_id)  REFERENCES semester_akademik (semester_id),
    CONSTRAINT chk_ip_range   CHECK (ips BETWEEN 0 AND 4 AND ipk BETWEEN 0 AND 4)
) ENGINE=InnoDB;

-- =====================================================================
-- J. SESSION & LOG AKTIVITAS (login / logout)
-- =====================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    session_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id      INT UNSIGNED    NOT NULL,
    token_hash   VARCHAR(128)    NOT NULL,                -- simpan hash token, bukan token asli
    ip_address   VARCHAR(45)     NULL,
    user_agent   VARCHAR(255)    NULL,
    login_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at   DATETIME        NOT NULL,
    logout_at    DATETIME        NULL,                    -- NULL = masih aktif / kedaluwarsa
    PRIMARY KEY (session_id),
    UNIQUE KEY uq_session_token (token_hash),
    KEY idx_session_user_logout (user_id, logout_at),
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS activity_log (
    log_id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id     INT UNSIGNED    NULL,                     -- NULL untuk login gagal / user tak dikenal
    aksi        VARCHAR(30)     NOT NULL,                 -- LOGIN, LOGOUT, INSERT, UPDATE, DELETE, APPROVE_KRS, INPUT_NILAI
    modul       VARCHAR(50)     NOT NULL,
    record_id   VARCHAR(50)     NULL,
    detail      JSON            NULL,
    ip_address  VARCHAR(45)     NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    KEY idx_log_user_waktu (user_id, created_at),
    KEY idx_log_modul_waktu (modul, created_at),
    CONSTRAINT fk_log_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
) ENGINE=InnoDB;