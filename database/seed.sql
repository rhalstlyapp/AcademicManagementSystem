
-- =====================================================================
-- seed.sql
-- Data awal / data contoh SIAKAD
--
-- Jalankan SETELAH:
--     1. schema.sql
--
-- Setelah itu:
--     2. triggers_views.sql
--     3. python database/create_admin.py
--
-- DBMS : MySQL 8.0+
--
-- Catatan:
-- - Admin TIDAK dibuat di sini.
-- - Akun admin dibuat menggunakan create_admin.py.
-- - Mahasiswa dapat login menggunakan Nama + NIM.
-- - Dosen menggunakan akun users dengan role dosen.
-- - Data contoh dibuat agar fitur akademik dapat langsung diuji.
-- =====================================================================

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

USE siakad;


-- =====================================================================
-- 1. ROLE
-- =====================================================================

INSERT IGNORE INTO roles (nama_role)
VALUES
    ('admin'),
    ('dosen'),
    ('mahasiswa');


-- =====================================================================
-- 2. SKALA NILAI
-- =====================================================================

INSERT IGNORE INTO skala_nilai
    (huruf_mutu, bobot_mutu, nilai_min, nilai_max, is_lulus)
VALUES
    ('A',  4.00, 85.00, 100.00, TRUE),
    ('AB', 3.50, 80.00,  84.99, TRUE),
    ('B',  3.00, 70.00,  79.99, TRUE),
    ('BC', 2.50, 65.00,  69.99, TRUE),
    ('C',  2.00, 55.00,  64.99, TRUE),
    ('D',  1.00, 40.00,  54.99, TRUE),
    ('E',  0.00,  0.00,  39.99, FALSE);


-- =====================================================================
-- 3. JURUSAN
-- =====================================================================

INSERT IGNORE INTO jurusan
    (kode_jurusan, nama_jurusan)
VALUES
    ('JAK', 'Akuntansi'),
    ('JAB', 'Administrasi Bisnis'),
    ('JKM', 'Kemaritiman'),
    ('JPR', 'Pariwisata'),
    ('JTI', 'Teknologi Informasi'),
    ('JDS', 'Desain'),
    ('JTK', 'Teknik Kimia'),
    ('JTS', 'Teknik Sipil'),
    ('JTE', 'Teknik Elektro'),
    ('JTM', 'Teknik Mesin');


-- =====================================================================
-- 4. PROGRAM STUDI
-- =====================================================================

INSERT IGNORE INTO program_studi
    (jurusan_id, kode_prodi, nama_prodi, jenjang)

SELECT
    j.jurusan_id,
    x.kode_prodi,
    x.nama_prodi,
    x.jenjang

FROM (
    SELECT 'JAK' AS kode_jurusan,
           'AK-D3' AS kode_prodi,
           'Akuntansi' AS nama_prodi,
           'D3' AS jenjang

    UNION ALL
    SELECT 'JAK',
           'AK-AM4',
           'Akuntansi Manajerial',
           'D4'

    UNION ALL
    SELECT 'JAK',
           'AK-KP4',
           'Keuangan Perbankan',
           'D4'

    UNION ALL
    SELECT 'JAB',
           'AB-MP4',
           'Manajemen Pemasaran',
           'D4'

    UNION ALL
    SELECT 'JAB',
           'AB-BD4',
           'Bisnis Digital',
           'D4'

    UNION ALL
    SELECT 'JKM',
           'KM-KPNK3',
           'KPNK',
           'D3'

    UNION ALL
    SELECT 'JKM',
           'KM-TEK3',
           'Teknik',
           'D3'

    UNION ALL
    SELECT 'JKM',
           'KM-NAU3',
           'Nautika',
           'D3'

    UNION ALL
    SELECT 'JPR',
           'PR-PAR3',
           'Pariwisata',
           'D3'

    UNION ALL
    SELECT 'JPR',
           'PR-UPW4',
           'Usaha Perjalanan',
           'D4'

    UNION ALL
    SELECT 'JTI',
           'TI',
           'Teknik Informatika',
           'D3'

    UNION ALL
    SELECT 'JTI',
           'TI-TK3',
           'Teknik Komputer',
           'D3'

    UNION ALL
    SELECT 'JTI',
           'TI-TIM4',
           'Teknik Informatika Multimedia',
           'D4'

    UNION ALL
    SELECT 'JTI',
           'TI-TRK4',
           'Teknologi Rekayasa Komputer',
           'D4'

    UNION ALL
    SELECT 'JDS',
           'DS-DP4',
           'Desain Produk',
           'D4'

    UNION ALL
    SELECT 'JDS',
           'DS-ARS4',
           'Arsitektur',
           'D4'

    UNION ALL
    SELECT 'JTK',
           'TK-POK3',
           'Petro & Oleo Kimia',
           'D3'

    UNION ALL
    SELECT 'JTK',
           'TK-TKI4',
           'Teknologi Kimia Industri',
           'D4'

    UNION ALL
    SELECT 'JTS',
           'TS-TRGB4',
           'Teknologi Rekayasa Konstruksi Bangunan Gedung',
           'D4'

    UNION ALL
    SELECT 'JTS',
           'TS-RJJ4',
           'Rekayasa Jalan & Jembatan',
           'D4'

    UNION ALL
    SELECT 'JTS',
           'TS-RKBA4',
           'Rekayasa Konstruksi Bangunan Air',
           'D4'

    UNION ALL
    SELECT 'JTE',
           'TE-TL3',
           'Teknik Listrik',
           'D3'

    UNION ALL
    SELECT 'JTE',
           'TE-TL4',
           'Teknik Listrik',
           'D4'

    UNION ALL
    SELECT 'JTM',
           'TM-PPM3',
           'Perawatan & Perbaikan Mesin',
           'D3'

    UNION ALL
    SELECT 'JTM',
           'TM-TMPP4',
           'Teknik Mesin Produksi & Perawatan',
           'D4'
) AS x

JOIN jurusan j
    ON j.kode_jurusan = x.kode_jurusan;


-- =====================================================================
-- 5. KURIKULUM
-- =====================================================================
--
-- Mata kuliah sekarang terhubung ke kurikulum.
-- Karena backend/mata_kuliah.py membutuhkan kurikulum_id,
-- data kurikulum harus dibuat sebelum mata kuliah.
-- =====================================================================

INSERT IGNORE INTO kurikulum
    (prodi_id, nama_kurikulum, tahun_berlaku, is_aktif)

SELECT
    p.prodi_id,
    CONCAT('Kurikulum ', p.nama_prodi, ' 2025'),
    2025,
    TRUE

FROM program_studi p

WHERE p.kode_prodi = 'TI';


-- =====================================================================
-- 6. SEMESTER AKADEMIK
-- =====================================================================

INSERT IGNORE INTO semester_akademik
    (
        kode_semester,
        tahun_akademik,
        jenis,
        tgl_mulai,
        tgl_selesai,
        tgl_mulai_krs,
        tgl_selesai_krs,
        is_aktif
    )

VALUES
    (
        '20251',
        '2025/2026',
        'Ganjil',
        '2025-09-01',
        '2026-02-28',
        '2025-08-01',
        '2025-08-31',
        FALSE
    ),

    (
        '20252',
        '2025/2026',
        'Genap',
        '2026-03-01',
        '2026-08-31',
        '2026-02-01',
        '2026-02-28',
        FALSE
    ),

    (
        '20261',
        '2026/2027',
        'Ganjil',
        '2026-09-01',
        '2027-02-28',
        '2026-08-01',
        '2026-08-31',
        TRUE
    );


-- =====================================================================
-- 7. MATA KULIAH
-- =====================================================================
--
-- Semua mata kuliah contoh berada di program studi Teknik Informatika.
-- Kurikulum diambil berdasarkan kode prodi TI.
-- =====================================================================

INSERT IGNORE INTO mata_kuliah
    (
        kurikulum_id,
        kode_mk,
        nama_mk,
        sks,
        semester_paket,
        jenis_mk
    )

SELECT
    k.kurikulum_id,
    x.kode_mk,
    x.nama_mk,
    x.sks,
    x.semester_paket,
    x.jenis_mk

FROM kurikulum k

JOIN program_studi p
    ON p.prodi_id = k.prodi_id

JOIN (
    SELECT
        'IF101' AS kode_mk,
        'Algoritma dan Pemrograman' AS nama_mk,
        3 AS sks,
        1 AS semester_paket,
        'Wajib' AS jenis_mk

    UNION ALL
    SELECT
        'IF102',
        'Basis Data',
        3,
        2,
        'Wajib'

    UNION ALL
    SELECT
        'IF103',
        'Matematika Diskrit',
        3,
        1,
        'Wajib'

    UNION ALL
    SELECT
        'IF104',
        'Struktur Data',
        3,
        2,
        'Wajib'

    UNION ALL
    SELECT
        'IF105',
        'Jaringan Komputer',
        2,
        3,
        'Wajib'

    UNION ALL
    SELECT
        'IF106',
        'Pemrograman Web',
        3,
        3,
        'Wajib'
) AS x

WHERE p.kode_prodi = 'TI';


-- =====================================================================
-- 8. PRASYARAT MATA KULIAH
-- =====================================================================

INSERT IGNORE INTO prasyarat_mk
    (mk_id, mk_prasyarat_id)

SELECT
    mk1.mk_id,
    mk2.mk_id

FROM mata_kuliah mk1
JOIN mata_kuliah mk2
    ON mk2.kode_mk = 'IF101'

WHERE mk1.kode_mk = 'IF104';


-- =====================================================================
-- 9. USER DOSEN CONTOH
-- =====================================================================
--
-- Password contoh:
--     Dosen123!
--
-- Password disimpan sebagai hash.
-- Hash bcrypt di bawah dapat digunakan sebagai password contoh.
--
-- Jika nantinya dosen dibuat melalui halaman admin, data ini
-- tidak wajib dipakai lagi.
-- =====================================================================

INSERT IGNORE INTO users
    (
        role_id,
        username,
        email,
        password_hash,
        is_active
    )

SELECT
    r.role_id,
    'dosen.ti',
    'dosen.ti@siakad.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCO7LJ9M8QKqK6K0W5V4J8K3Y4x6mV2L5u',
    TRUE

FROM roles r

WHERE r.nama_role = 'dosen';


-- =====================================================================
-- 10. PROFIL DOSEN
-- =====================================================================

INSERT IGNORE INTO dosen
    (
        user_id,
        prodi_id,
        nidn,
        nip,
        nama_lengkap,
        jenis_kelamin,
        status
    )

SELECT
    u.user_id,
    p.prodi_id,
    '0012345678',
    '198501012010011001',
    'Dr. Budi Santoso, S.Kom., M.Kom.',
    'L',
    'Aktif'

FROM users u

JOIN roles r
    ON r.role_id = u.role_id

JOIN program_studi p
    ON p.kode_prodi = 'TI'

WHERE
    r.nama_role = 'dosen'
    AND u.username = 'dosen.ti';


-- =====================================================================
-- 11. USER MAHASISWA CONTOH
-- =====================================================================
--
-- Mahasiswa publik menggunakan:
--
--     username = NIM
--     password_hash = NULL
--
-- Login dilakukan menggunakan:
--
--     Nama + NIM
-- =====================================================================

INSERT IGNORE INTO users
    (
        role_id,
        username,
        email,
        password_hash,
        is_active
    )

SELECT
    r.role_id,
    x.nim,
    NULL,
    NULL,
    TRUE

FROM roles r

JOIN (
    SELECT '2501001' AS nim
    UNION ALL SELECT '2501002'
    UNION ALL SELECT '2502001'
) AS x

WHERE r.nama_role = 'mahasiswa';


-- =====================================================================
-- 12. PROFIL MAHASISWA
-- =====================================================================

INSERT IGNORE INTO mahasiswa
    (
        user_id,
        prodi_id,
        dosen_pa_id,
        nim,
        nama_lengkap,
        jenis_kelamin,
        tempat_lahir,
        tanggal_lahir,
        agama,
        nik,
        alamat,
        no_hp,
        nama_ayah,
        nama_ibu,
        angkatan,
        status_mahasiswa
    )

SELECT
    u.user_id,
    p.prodi_id,
    d.dosen_id,
    x.nim,
    x.nama_lengkap,
    x.jenis_kelamin,
    x.tempat_lahir,
    x.tanggal_lahir,
    x.agama,
    x.nik,
    x.alamat,
    x.no_hp,
    x.nama_ayah,
    x.nama_ibu,
    x.angkatan,
    'Aktif'

FROM (
    SELECT
        '2501001' AS nim,
        'Budi Santoso' AS nama_lengkap,
        'L' AS jenis_kelamin,
        'Samarinda' AS tempat_lahir,
        '2006-03-14' AS tanggal_lahir,
        'Islam' AS agama,
        '6400000000000001' AS nik,
        'Samarinda' AS alamat,
        '081234567890' AS no_hp,
        'Joko Santoso' AS nama_ayah,
        'Siti Aminah' AS nama_ibu,
        2025 AS angkatan,
        'TI' AS kode_prodi

    UNION ALL

    SELECT
        '2501002',
        'Siti Aminah',
        'P',
        'Samarinda',
        '2006-07-02',
        'Islam',
        '6400000000000002',
        'Samarinda',
        '081234567891',
        'Ahmad Amin',
        'Rina Aminah',
        2025,
        'TI'

    UNION ALL

    SELECT
        '2502001',
        'Andi Wijaya',
        'L',
        'Balikpapan',
        '2005-11-21',
        'Islam',
        '6471000000000001',
        'Balikpapan',
        '081234567892',
        'Wijaya',
        'Dewi Wijaya',
        2025,
        'TI'
) AS x

JOIN users u
    ON u.username = x.nim

JOIN roles r
    ON r.role_id = u.role_id
    AND r.nama_role = 'mahasiswa'

JOIN program_studi p
    ON p.kode_prodi = x.kode_prodi

LEFT JOIN dosen d
    ON d.prodi_id = p.prodi_id
    AND d.status = 'Aktif';


-- =====================================================================
-- 13. KELAS
-- =====================================================================
--
-- Membuat contoh kelas untuk mata kuliah.
-- Dosen pengajar dihubungkan melalui kelas_dosen.
-- =====================================================================

INSERT IGNORE INTO kelas
    (
        mk_id,
        semester_id,
        nama_kelas,
        kuota
    )

SELECT
    mk.mk_id,
    s.semester_id,
    'A',
    40

FROM mata_kuliah mk

JOIN semester_akademik s
    ON s.kode_semester = '20261'

WHERE mk.kode_mk IN ('IF101', 'IF102', 'IF103');


-- =====================================================================
-- 14. HUBUNGKAN DOSEN DENGAN KELAS
-- =====================================================================

INSERT IGNORE INTO kelas_dosen
    (
        kelas_id,
        dosen_id,
        peran
    )

SELECT
    k.kelas_id,
    d.dosen_id,
    'Koordinator'

FROM kelas k

JOIN mata_kuliah mk
    ON mk.mk_id = k.mk_id

JOIN dosen d
    ON d.nidn = '0012345678'

JOIN semester_akademik s
    ON s.semester_id = k.semester_id

WHERE
    s.kode_semester = '20261'
    AND mk.kode_mk IN ('IF101', 'IF102', 'IF103');


-- =====================================================================
-- 15. KRS MAHASISWA
-- =====================================================================

INSERT IGNORE INTO krs
    (
        mahasiswa_id,
        semester_id,
        status,
        tanggal_pengajuan,
        tanggal_persetujuan
    )

SELECT
    m.mahasiswa_id,
    s.semester_id,
    'Disetujui',
    NOW(),
    NOW()

FROM mahasiswa m

JOIN semester_akademik s
    ON s.kode_semester = '20261'

WHERE m.nim IN ('2501001', '2501002');


-- =====================================================================
-- 16. DETAIL KRS
-- =====================================================================

INSERT IGNORE INTO krs_detail
    (
        krs_id,
        kelas_id
    )

SELECT
    k.krs_id,
    kl.kelas_id

FROM krs k

JOIN mahasiswa m
    ON m.mahasiswa_id = k.mahasiswa_id

JOIN semester_akademik s
    ON s.semester_id = k.semester_id

JOIN kelas kl
    ON kl.semester_id = s.semester_id

WHERE
    m.nim IN ('2501001', '2501002')
    AND s.kode_semester = '20261';


-- =====================================================================
-- 17. NILAI MAHASISWA
-- =====================================================================
--
-- Backend sekarang menggunakan tabel:
--
--     nilai_mahasiswa
--
-- bukan tabel "nilai" lama.
--
-- Nilai langsung menyimpan:
--     mahasiswa
--     mata kuliah
--     semester
--     skala nilai
--     nilai angka
--     dosen penginput
-- =====================================================================

INSERT IGNORE INTO nilai_mahasiswa
    (
        mahasiswa_id,
        mk_id,
        semester_id,
        skala_id,
        nilai_angka,
        is_final,
        diinput_oleh,
        finalized_at
    )

SELECT
    m.mahasiswa_id,
    mk.mk_id,
    s.semester_id,
    sn.skala_id,
    x.nilai_angka,
    TRUE,
    d.dosen_id,
    NOW()

FROM (
    SELECT '2501001' AS nim, 'IF101' AS kode_mk, '20251' AS kode_semester, 55.00 AS nilai_angka
    UNION ALL
    SELECT '2501001', 'IF102', '20251', 88.00
    UNION ALL
    SELECT '2501001', 'IF103', '20251', 82.00

    UNION ALL
    SELECT '2501001', 'IF101', '20252', 78.00
    UNION ALL
    SELECT '2501001', 'IF104', '20252', 70.00
    UNION ALL
    SELECT '2501001', 'IF105', '20252', 90.00

    UNION ALL
    SELECT '2501002', 'IF101', '20251', 92.00
    UNION ALL
    SELECT '2501002', 'IF102', '20251', 72.00
    UNION ALL
    SELECT '2501002', 'IF103', '20251', 60.00

    UNION ALL
    SELECT '2502001', 'IF101', '20251', 35.00
    UNION ALL
    SELECT '2502001', 'IF102', '20251', 62.00
    UNION ALL
    SELECT '2502001', 'IF106', '20251', 90.00
) AS x

JOIN mahasiswa m
    ON m.nim = x.nim

JOIN mata_kuliah mk
    ON mk.kode_mk = x.kode_mk

JOIN semester_akademik s
    ON s.kode_semester = x.kode_semester

JOIN skala_nilai sn
    ON x.nilai_angka BETWEEN sn.nilai_min AND sn.nilai_max

LEFT JOIN dosen d
    ON d.nidn = '0012345678';


-- =====================================================================
-- 18. CONTOH TUGAS MAHASISWA
-- =====================================================================
--
-- Backend tugas.py menggunakan tabel:
--
--     tugas_mahasiswa
--
-- Data dibuat untuk mahasiswa 2501001.
-- =====================================================================

INSERT IGNORE INTO tugas_mahasiswa
    (
        mahasiswa_id,
        judul,
        catatan,
        tanggal,
        selesai
    )

SELECT
    m.mahasiswa_id,
    x.judul,
    x.catatan,
    x.tanggal,
    x.selesai

FROM mahasiswa m

JOIN (
    SELECT
        '2501001' AS nim,
        'Mengerjakan laporan Basis Data' AS judul,
        'Selesaikan bagian ERD dan SQL.' AS catatan,
        '2026-11-25' AS tanggal,
        FALSE AS selesai

    UNION ALL

    SELECT
        '2501001',
        'Belajar Python',
        'Review function, list, dictionary, dan loop.',
        '2026-11-27',
        FALSE

    UNION ALL

    SELECT
        '2501001',
        'Submit tugas pemrograman',
        'Upload project ke GitHub.',
        '2026-11-30',
        FALSE
) AS x
    ON x.nim = m.nim;


-- =====================================================================
-- SELESAI
-- =====================================================================

SELECT 'Seed database selesai.' AS message;
