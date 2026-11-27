-- Izinkan pendaftaran mahasiswa dengan field pada form login saat ini:
-- Nama, NIM, jurusan, dan program studi. Data profil lain bisa dilengkapi admin.
USE siakad;

ALTER TABLE users
    MODIFY email VARCHAR(100) NULL,
    MODIFY password_hash VARCHAR(255) NULL;

ALTER TABLE mahasiswa
    MODIFY dosen_pa_id INT UNSIGNED NULL,
    MODIFY jenis_kelamin ENUM('L','P') NULL,
    MODIFY tanggal_lahir DATE NULL,
    MODIFY angkatan SMALLINT UNSIGNED NULL;

ALTER TABLE mahasiswa
    DROP CHECK chk_mhs_angkatan,
    ADD CONSTRAINT chk_mhs_angkatan
        CHECK (angkatan IS NULL OR angkatan BETWEEN 1990 AND 2100);
