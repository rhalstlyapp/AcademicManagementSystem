-- =====================================================================
-- View transkrip, IPS, dan IPK untuk skema KRS/nilai_akhir.
-- Jalankan setelah schema.sql dan seed.sql. Memerlukan MySQL 8.0+.
-- Hanya KRS disetujui dan nilai akhir yang sudah difinalisasi dihitung.
-- IPK memakai nilai terbaik mahasiswa untuk setiap mata kuliah.
-- =====================================================================

USE siakad;

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
    na.nilai_angka AS nilai_akhir,
    sn.huruf_mutu,
    sn.bobot_mutu,
    sn.is_lulus,
    (mk.sks * sn.bobot_mutu) AS mutu,
    CASE WHEN sn.is_lulus THEN 'Lulus' ELSE 'Tidak Lulus' END AS status_kelulusan
FROM krs_detail kd
JOIN krs k ON k.krs_id = kd.krs_id
JOIN mahasiswa m ON m.mahasiswa_id = k.mahasiswa_id
JOIN kelas kl ON kl.kelas_id = kd.kelas_id
JOIN mata_kuliah mk ON mk.mk_id = kl.mk_id
JOIN semester_akademik sa ON sa.semester_id = k.semester_id
JOIN nilai_akhir na ON na.krs_detail_id = kd.krs_detail_id
JOIN skala_nilai sn ON sn.skala_id = na.skala_id
WHERE k.status = 'Disetujui' AND na.is_final = TRUE;

CREATE OR REPLACE VIEW v_ips AS
SELECT
    ranked.mahasiswa_id,
    ranked.semester_id,
    ranked.kode_semester,
    ranked.tahun_akademik,
    SUM(ranked.sks) AS sks_diambil,
    SUM(CASE WHEN ranked.is_lulus THEN ranked.sks ELSE 0 END) AS sks_lulus,
    SUM(ranked.mutu) AS total_mutu,
    ROUND(SUM(ranked.mutu) / NULLIF(SUM(ranked.sks), 0), 2) AS ips
FROM (
    SELECT t.*,
           ROW_NUMBER() OVER (
               PARTITION BY t.mahasiswa_id, t.semester_id, t.mk_id
               ORDER BY t.bobot_mutu DESC, t.nilai_akhir DESC, t.kode_semester DESC
           ) AS percobaan
    FROM v_transkrip t
) AS ranked
WHERE ranked.percobaan = 1
GROUP BY ranked.mahasiswa_id, ranked.semester_id, ranked.kode_semester, ranked.tahun_akademik;

CREATE OR REPLACE VIEW v_ipk AS
SELECT
    best.mahasiswa_id,
    best.nim,
    best.nama_lengkap,
    SUM(best.sks) AS total_sks,
    SUM(CASE WHEN best.is_lulus THEN best.sks ELSE 0 END) AS total_sks_lulus,
    SUM(best.mutu) AS total_mutu,
    ROUND(SUM(best.mutu) / NULLIF(SUM(best.sks), 0), 2) AS ipk
FROM (
    SELECT t.*,
           ROW_NUMBER() OVER (
               PARTITION BY t.mahasiswa_id, t.mk_id
               ORDER BY t.bobot_mutu DESC, t.nilai_akhir DESC, t.kode_semester DESC
           ) AS percobaan
    FROM v_transkrip t
) AS best
WHERE best.percobaan = 1
GROUP BY best.mahasiswa_id, best.nim, best.nama_lengkap;
