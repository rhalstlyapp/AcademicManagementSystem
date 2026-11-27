-- ============================================================
-- add_profile_features.sql
-- Fitur Profil + Pengajuan Perubahan NIM
-- ============================================================

USE siakad;


-- ============================================================
-- PENGAJUAN PERUBAHAN NIM
-- ============================================================

CREATE TABLE IF NOT EXISTS pengajuan_perubahan_nim (
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

    KEY idx_pengajuan_mahasiswa (
        mahasiswa_id
    ),

    KEY idx_pengajuan_status (
        status
    ),

    KEY idx_pengajuan_admin (
        diproses_oleh
    ),

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


SELECT
    'Tabel pengajuan_perubahan_nim berhasil dibuat.' AS status;