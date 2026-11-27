-- Migrasi satu kali untuk database siakad lama yang masih memakai fakultas.
-- Backup database terlebih dahulu. Jangan jalankan pada database yang sudah
-- memakai jurusan_id.

USE siakad;

CREATE TABLE IF NOT EXISTS jurusan (
    jurusan_id    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    kode_jurusan  VARCHAR(10)  NOT NULL,
    nama_jurusan  VARCHAR(100) NOT NULL,
    PRIMARY KEY (jurusan_id),
    UNIQUE KEY uq_jurusan_kode (kode_jurusan)
) ENGINE=InnoDB;

INSERT INTO jurusan (kode_jurusan, nama_jurusan)
SELECT kode_fakultas, nama_fakultas
FROM fakultas
ON DUPLICATE KEY UPDATE nama_jurusan = VALUES(nama_jurusan);

ALTER TABLE program_studi
    DROP FOREIGN KEY fk_prodi_fakultas,
    DROP INDEX idx_prodi_fakultas,
    ADD COLUMN jurusan_id INT UNSIGNED NULL AFTER prodi_id;

UPDATE program_studi p
JOIN fakultas f ON f.fakultas_id = p.fakultas_id
JOIN jurusan j ON j.kode_jurusan = f.kode_fakultas
SET p.jurusan_id = j.jurusan_id;

ALTER TABLE program_studi
    MODIFY jurusan_id INT UNSIGNED NOT NULL,
    ADD KEY idx_prodi_jurusan (jurusan_id),
    ADD CONSTRAINT fk_prodi_jurusan
        FOREIGN KEY (jurusan_id) REFERENCES jurusan (jurusan_id),
    DROP COLUMN fakultas_id;

DROP TABLE fakultas;
