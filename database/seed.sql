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
INSERT INTO jurusan (kode_jurusan, nama_jurusan) VALUES
    ('TEK', 'Teknik')
ON DUPLICATE KEY UPDATE nama_jurusan = VALUES(nama_jurusan);

INSERT INTO program_studi (jurusan_id, kode_prodi, nama_prodi, jenjang)
SELECT j.jurusan_id, 'TI', 'Teknik Informatika', 'S1'
FROM jurusan j
WHERE j.kode_jurusan = 'TEK'
ON DUPLICATE KEY UPDATE nama_prodi = VALUES(nama_prodi);

INSERT INTO kurikulum (prodi_id, nama_kurikulum, tahun_berlaku, is_aktif)
SELECT p.prodi_id, 'Kurikulum 2026', 2026, TRUE
FROM program_studi p
WHERE p.kode_prodi = 'TI'
ON DUPLICATE KEY UPDATE is_aktif = VALUES(is_aktif);

INSERT INTO mata_kuliah (kurikulum_id, kode_mk, nama_mk, sks, semester_paket, jenis_mk)
SELECT k.kurikulum_id, contoh.kode_mk, contoh.nama_mk, contoh.sks, contoh.semester_paket, 'Wajib'
FROM kurikulum k
JOIN program_studi p ON p.prodi_id = k.prodi_id
JOIN (
    SELECT 'TI101' AS kode_mk, 'Algoritma dan Pemrograman' AS nama_mk, 3 AS sks, 1 AS semester_paket
    UNION ALL SELECT 'TI102', 'Matematika Diskrit', 3, 1
    UNION ALL SELECT 'TI201', 'Basis Data', 3, 3
) AS contoh
WHERE p.kode_prodi = 'TI' AND k.nama_kurikulum = 'Kurikulum 2026'
ON DUPLICATE KEY UPDATE
    nama_mk = VALUES(nama_mk),
    sks = VALUES(sks),
    semester_paket = VALUES(semester_paket);

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
