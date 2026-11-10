-- =====================================================================
-- seed.sql : Data awal SIAKAD
-- Jalankan SETELAH schema.sql. Aman dijalankan berulang kali.
-- Akun admin TIDAK dibuat di sini; gunakan: python database/create_admin.py
-- =====================================================================

USE siakad;

-- ---------------------------------------------------------------------
-- 1. Role
-- ---------------------------------------------------------------------
INSERT INTO roles (nama_role) VALUES
    ('admin'),
    ('dosen'),
    ('mahasiswa')
ON DUPLICATE KEY UPDATE nama_role = nama_role;

-- ---------------------------------------------------------------------
-- 2. Skala nilai (huruf mutu, bobot, rentang nilai angka)
--    Sesuaikan dengan aturan kampus. D dianggap lulus; ubah is_lulus bila perlu.
-- ---------------------------------------------------------------------
INSERT INTO skala_nilai (huruf_mutu, bobot_mutu, nilai_min, nilai_max, is_lulus) VALUES
    ('A',  4.00, 85.00, 100.00, TRUE),
    ('AB', 3.50, 80.00,  84.99, TRUE),
    ('B',  3.00, 70.00,  79.99, TRUE),
    ('BC', 2.50, 65.00,  69.99, TRUE),
    ('C',  2.00, 55.00,  64.99, TRUE),
    ('D',  1.00, 40.00,  54.99, TRUE),
    ('E',  0.00,  0.00,  39.99, FALSE)
ON DUPLICATE KEY UPDATE
    bobot_mutu = VALUES(bobot_mutu),
    nilai_min  = VALUES(nilai_min),
    nilai_max  = VALUES(nilai_max),
    is_lulus   = VALUES(is_lulus);

-- ---------------------------------------------------------------------
-- 3. Aturan batas SKS berdasarkan IPS semester sebelumnya
--    Mahasiswa semester 1 (belum punya IPS) memakai batas default di backend.
--    Hanya diisi jika tabel masih kosong, agar tidak terduplikasi.
-- ---------------------------------------------------------------------
INSERT INTO aturan_batas_sks (ips_min, ips_max, sks_maks)
SELECT t.ips_min, t.ips_max, t.sks_maks
FROM (
    SELECT 3.00 AS ips_min, 4.00 AS ips_max, 24 AS sks_maks
    UNION ALL SELECT 2.50, 2.99, 21
    UNION ALL SELECT 2.00, 2.49, 18
    UNION ALL SELECT 0.00, 1.99, 15
) AS t
WHERE NOT EXISTS (SELECT 1 FROM aturan_batas_sks);

-- ---------------------------------------------------------------------
-- 4. Contoh data master (untuk uji coba; ganti sesuai kampus kamu)
-- ---------------------------------------------------------------------
INSERT INTO fakultas (kode_fakultas, nama_fakultas) VALUES
    ('FT', 'Fakultas Teknik')
ON DUPLICATE KEY UPDATE nama_fakultas = VALUES(nama_fakultas);

INSERT INTO program_studi (fakultas_id, kode_prodi, nama_prodi, jenjang)
SELECT f.fakultas_id, 'TI', 'Teknik Informatika', 'S1'
FROM fakultas f
WHERE f.kode_fakultas = 'FT'
ON DUPLICATE KEY UPDATE nama_prodi = VALUES(nama_prodi);

-- Periode KRS sengaja dibuat panjang agar fitur KRS bisa diuji kapan saja.
INSERT INTO semester_akademik
    (kode_semester, tahun_akademik, jenis, tgl_mulai, tgl_selesai, tgl_mulai_krs, tgl_selesai_krs, is_aktif)
VALUES
    ('20261', '2026/2027', 'Ganjil', '2026-09-01', '2027-01-31', '2026-08-15', '2026-12-31', TRUE)
ON DUPLICATE KEY UPDATE tahun_akademik = tahun_akademik;

INSERT INTO ruang (kode_ruang, nama_ruang, gedung, kapasitas, jenis) VALUES
    ('R101', 'Ruang 101',     'Gedung A', 40, 'Kelas'),
    ('R102', 'Ruang 102',     'Gedung A', 40, 'Kelas'),
    ('LAB1', 'Lab Komputer 1','Gedung B', 30, 'Lab')
ON DUPLICATE KEY UPDATE nama_ruang = VALUES(nama_ruang);