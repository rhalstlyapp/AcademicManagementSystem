-- Data master jurusan dan program studi kampus.
-- Jalankan setelah schema.sql dan migrate_fakultas_to_jurusan.sql.
-- Aman dijalankan ulang berdasarkan kode jurusan/prodi.

USE siakad;

-- migrate_fakultas_to_jurusan.sql memindahkan nama fakultas ke jurusan.
-- Ubah baris hasil migrasi yang lama menjadi data jurusan sebenarnya.
UPDATE jurusan
SET kode_jurusan = 'JTI', nama_jurusan = 'Teknologi Informasi'
WHERE kode_jurusan = 'FT';

INSERT INTO jurusan (kode_jurusan, nama_jurusan) VALUES
    ('JAK', 'Akuntansi'),
    ('JAB', 'Administrasi Bisnis'),
    ('JKM', 'Kemaritiman'),
    ('JPR', 'Pariwisata'),
    ('JTI', 'Teknologi Informasi'),
    ('JDS', 'Desain'),
    ('JTK', 'Teknik Kimia'),
    ('JTS', 'Teknik Sipil'),
    ('JTE', 'Teknik Elektro'),
    ('JTM', 'Teknik Mesin')
ON DUPLICATE KEY UPDATE nama_jurusan = VALUES(nama_jurusan);

-- Kode TI sudah ada dari data lama; pakai kembali untuk D3 Teknik Informatika.
UPDATE program_studi p
JOIN jurusan j ON j.kode_jurusan = 'JTI'
SET p.jurusan_id = j.jurusan_id,
    p.nama_prodi = 'Teknik Informatika',
    p.jenjang = 'D3'
WHERE p.kode_prodi = 'TI';

INSERT INTO program_studi (jurusan_id, kode_prodi, nama_prodi, jenjang)
SELECT j.jurusan_id, t.kode_prodi, t.nama_prodi, t.jenjang
FROM (
    SELECT 'JAK' AS kode_jurusan, 'AK-D3' AS kode_prodi, 'Akuntansi' AS nama_prodi, 'D3' AS jenjang
    UNION ALL SELECT 'JAK', 'AK-AM4', 'Akuntansi Manajerial', 'D4'
    UNION ALL SELECT 'JAK', 'AK-KP4', 'Keuangan Perbankan', 'D4'
    UNION ALL SELECT 'JAB', 'AB-MP4', 'Manajemen Pemasaran', 'D4'
    UNION ALL SELECT 'JAB', 'AB-BD4', 'Bisnis Digital', 'D4'
    UNION ALL SELECT 'JKM', 'KM-KPNK3', 'KPNK', 'D3'
    UNION ALL SELECT 'JKM', 'KM-TEK3', 'Teknik', 'D3'
    UNION ALL SELECT 'JKM', 'KM-NAU3', 'Nautika', 'D3'
    UNION ALL SELECT 'JPR', 'PR-PAR3', 'Pariwisata', 'D3'
    UNION ALL SELECT 'JPR', 'PR-UPW4', 'Usaha Perjalanan', 'D4'
    UNION ALL SELECT 'JTI', 'TI-TK3', 'Teknik Komputer', 'D3'
    UNION ALL SELECT 'JTI', 'TI-TIM4', 'Teknik Informatika Multimedia', 'D4'
    UNION ALL SELECT 'JTI', 'TI-TRK4', 'Teknologi Rekayasa Komputer', 'D4'
    UNION ALL SELECT 'JDS', 'DS-DP4', 'Desain Produk', 'D4'
    UNION ALL SELECT 'JDS', 'DS-ARS4', 'Arsitektur', 'D4'
    UNION ALL SELECT 'JTK', 'TK-POK3', 'Petro & Oleo Kimia', 'D3'
    UNION ALL SELECT 'JTK', 'TK-TKI4', 'Teknologi Kimia Industri', 'D4'
    UNION ALL SELECT 'JTS', 'TS-TRGB4', 'Teknologi Rekayasa Konstruksi Bangunan Gedung', 'D4'
    UNION ALL SELECT 'JTS', 'TS-RJJ4', 'Rekayasa Jalan & Jembatan', 'D4'
    UNION ALL SELECT 'JTS', 'TS-RKBA4', 'Rekayasa Konstruksi Bangunan Air', 'D4'
    UNION ALL SELECT 'JTE', 'TE-TL3', 'Teknik Listrik', 'D3'
    UNION ALL SELECT 'JTE', 'TE-TL4', 'Teknik Listrik', 'D4'
    UNION ALL SELECT 'JTM', 'TM-PPM3', 'Perawatan & Perbaikan Mesin', 'D3'
    UNION ALL SELECT 'JTM', 'TM-TMPP4', 'Teknik Mesin Produksi & Perawatan', 'D4'
) AS t
JOIN jurusan j ON j.kode_jurusan = t.kode_jurusan
ON DUPLICATE KEY UPDATE
    jurusan_id = VALUES(jurusan_id),
    nama_prodi = VALUES(nama_prodi),
    jenjang = VALUES(jenjang);
