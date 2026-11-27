-- Jalankan pada database siakad dengan skema akademik lengkap.
-- Membuat penyimpanan agenda pribadi mahasiswa tanpa mengubah data akademik lain.

USE siakad;

CREATE TABLE IF NOT EXISTS tugas_mahasiswa (
    tugas_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    mahasiswa_id  INT UNSIGNED NOT NULL,
    judul         VARCHAR(180) NOT NULL,
    catatan       VARCHAR(1000) NULL,
    tanggal       DATE NOT NULL,
    selesai       BOOLEAN NOT NULL DEFAULT FALSE,
    dibuat_pada   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    diubah_pada   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (tugas_id),
    KEY idx_tugas_mahasiswa_tanggal (mahasiswa_id, tanggal),
    CONSTRAINT fk_tugas_mahasiswa
        FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa (mahasiswa_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
