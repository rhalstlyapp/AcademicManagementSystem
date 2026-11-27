
-- =====================================================================
-- triggers_views.sql
-- SIAKAD - Trigger / Migration / View untuk Nilai, Transkrip, IPS, IPK
--
-- DBMS : MySQL 8.0.16+
--
-- Catatan:
-- 1. Tabel nilai_mahasiswa SUDAH dibuat di schema.sql.
-- 2. File ini TIDAK membuat ulang tabel nilai_mahasiswa.
-- 3. File ini membuat/memperbarui VIEW yang digunakan backend.
-- 4. View disesuaikan dengan backend/ipk.py dan backend/nilai.py.
-- =====================================================================


USE siakad;


-- =====================================================================
-- BAGIAN 1
-- MIGRASI DATA NILAI LAMA
-- =====================================================================
--
-- Bagian ini digunakan apabila database masih memiliki data pada:
--     nilai_akhir
--     krs_detail
--     krs
--     kelas
--
-- Data nilai final akan dimasukkan ke:
--     nilai_mahasiswa
--
-- Karena menggunakan INSERT IGNORE, data yang sudah ada tidak akan
-- dimasukkan ulang apabila melanggar UNIQUE:
--
--     (mahasiswa_id, mk_id, semester_id)
--
-- =====================================================================

-- =====================================================================
-- MIGRASI NILAI_AKHIR -> NILAI_MAHASISWA
-- =====================================================================

INSERT IGNORE INTO nilai_mahasiswa (
    mahasiswa_id,
    mk_id,
    semester_id,
    nilai_angka,
    skala_id,
    is_final,
    diinput_oleh,
    finalized_at
)
SELECT
    k.mahasiswa_id,
    kl.mk_id,
    k.semester_id,
    na.nilai_angka,
    na.skala_id,
    TRUE,
    na.diinput_oleh,
    na.finalized_at
FROM nilai_akhir na

JOIN krs_detail kd
    ON kd.krs_detail_id = na.krs_detail_id

JOIN krs k
    ON k.krs_id = kd.krs_id

JOIN kelas kl
    ON kl.kelas_id = kd.kelas_id

WHERE na.is_final = TRUE
  AND k.status = 'Disetujui';


-- =====================================================================
-- BAGIAN 2
-- VIEW TRANSKRIP
-- =====================================================================
--
-- Digunakan oleh:
--     backend/nilai.py
--     backend/ipk.py
--
-- Menampilkan nilai final mahasiswa.
--
-- Kolom penting yang harus tersedia:
--     mahasiswa_id
--     nim
--     nama_lengkap
--     mk_id
--     kode_mk
--     nama_mk
--     sks
--     semester_id
--     kode_semester
--     tahun_akademik
--     nilai_akhir
--     huruf_mutu
--     bobot_mutu
--     is_lulus
--     mutu
--     status_kelulusan
--
-- =====================================================================

CREATE OR REPLACE VIEW v_transkrip AS
SELECT
    m.mahasiswa_id,
    m.nim,
    m.nama_lengkap,

    mk.mk_id,
    mk.kode_mk,
    mk.nama_mk,
    mk.sks,

    sa.semester_id,
    sa.kode_semester,
    sa.tahun_akademik,

    nm.nilai_angka AS nilai_akhir,

    sn.huruf_mutu,
    sn.bobot_mutu,
    sn.is_lulus,

    (mk.sks * sn.bobot_mutu) AS mutu,

    CASE
        WHEN sn.is_lulus = TRUE
            THEN 'Lulus'
        ELSE 'Tidak Lulus'
    END AS status_kelulusan

FROM nilai_mahasiswa nm

JOIN mahasiswa m
    ON m.mahasiswa_id = nm.mahasiswa_id

JOIN mata_kuliah mk
    ON mk.mk_id = nm.mk_id

JOIN semester_akademik sa
    ON sa.semester_id = nm.semester_id

JOIN skala_nilai sn
    ON sn.skala_id = nm.skala_id

WHERE nm.is_final = TRUE;


-- =====================================================================
-- BAGIAN 3
-- VIEW IPS
-- =====================================================================
--
-- IPS = Indeks Prestasi Semester
--
-- Jika seorang mahasiswa mengambil mata kuliah yang sama lebih dari
-- sekali, hanya nilai terbaik yang digunakan untuk perhitungan IPS.
--
-- Penentuan nilai terbaik:
--     1. bobot_mutu terbesar
--     2. jika sama, nilai_angka terbesar
--     3. jika masih sama, semester terbaru
--
-- View ini juga menyediakan "nim" karena backend/ipk.py menggunakan:
--
--     WHERE nim = %s
--
-- =====================================================================

CREATE OR REPLACE VIEW v_ips AS

SELECT
    ranked.mahasiswa_id,
    ranked.nim,
    ranked.semester_id,
    ranked.kode_semester,
    ranked.tahun_akademik,

    SUM(ranked.sks) AS sks_diambil,

    SUM(
        CASE
            WHEN ranked.is_lulus = TRUE
                THEN ranked.sks
            ELSE 0
        END
    ) AS sks_lulus,

    SUM(ranked.mutu) AS total_mutu,

    ROUND(
        SUM(ranked.mutu)
        / NULLIF(SUM(ranked.sks), 0),
        2
    ) AS ips

FROM (
    SELECT
        t.*,

        ROW_NUMBER() OVER (
            PARTITION BY
                t.mahasiswa_id,
                t.semester_id,
                t.mk_id

            ORDER BY
                t.bobot_mutu DESC,
                t.nilai_akhir DESC,
                t.kode_semester DESC
        ) AS percobaan

    FROM v_transkrip t
) AS ranked

WHERE ranked.percobaan = 1

GROUP BY
    ranked.mahasiswa_id,
    ranked.nim,
    ranked.semester_id,
    ranked.kode_semester,
    ranked.tahun_akademik;


-- =====================================================================
-- BAGIAN 4
-- VIEW IPK
-- =====================================================================
--
-- IPK = Indeks Prestasi Kumulatif
--
-- Untuk setiap mata kuliah yang pernah diambil beberapa kali,
-- hanya nilai terbaik yang digunakan.
--
-- Contoh:
--
-- Semester 1:
--     Basis Data = C
--
-- Semester 2:
--     Basis Data = A
--
-- Maka untuk IPK, yang digunakan adalah A.
--
-- =====================================================================

CREATE OR REPLACE VIEW v_ipk AS

SELECT
    best.mahasiswa_id,
    best.nim,
    best.nama_lengkap,

    SUM(best.sks) AS total_sks,

    SUM(
        CASE
            WHEN best.is_lulus = TRUE
                THEN best.sks
            ELSE 0
        END
    ) AS total_sks_lulus,

    SUM(best.mutu) AS total_mutu,

    ROUND(
        SUM(best.mutu)
        / NULLIF(SUM(best.sks), 0),
        2
    ) AS ipk

FROM (
    SELECT
        t.*,

        ROW_NUMBER() OVER (
            PARTITION BY
                t.mahasiswa_id,
                t.mk_id

            ORDER BY
                t.bobot_mutu DESC,
                t.nilai_akhir DESC,
                t.kode_semester DESC
        ) AS percobaan

    FROM v_transkrip t
) AS best

WHERE best.percobaan = 1

GROUP BY
    best.mahasiswa_id,
    best.nim,
    best.nama_lengkap;


-- =====================================================================
-- BAGIAN 5
-- CEK VIEW
-- =====================================================================
--
-- Query berikut hanya untuk pengecekan.
-- Tidak wajib dijalankan jika file ini dijalankan otomatis.
--
-- Contoh:
--
-- SELECT * FROM v_transkrip;
-- SELECT * FROM v_ips;
-- SELECT * FROM v_ipk;
--
-- =====================================================================
