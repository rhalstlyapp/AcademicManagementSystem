"""Uji backend ke MySQL sungguhan. Hanya MEMBACA, tidak mengubah data
(kecuali mencatat waktu login terakhir admin).
Jalankan dari folder proyek:  python test_backend.py
Perlu: Laragon menyala, schema.sql + seed.sql + triggers_views.sql sudah diimpor,
dan akun admin sudah dibuat (python database/create_admin.py).
Hapus file ini bila sudah tidak diperlukan."""
from getpass import getpass

from backend import auth, ipk, mahasiswa, nilai
from utils.validators import AksesDitolak, AppError


def cek(label, ok):
    print(("[OK]   " if ok else "[BEDA] ") + label)


def hampir(a, b):
    return a is not None and abs(float(a) - b) < 0.005


try:
    # --- data publik formulir daftar (tanpa login) ---
    jurusan = auth.daftar_jurusan()
    cek(f"dropdown jurusan terbaca tanpa login ({len(jurusan)} jurusan)", len(jurusan) >= 1)
    if jurusan:
        prodi = auth.daftar_prodi(jurusan[0]["jurusan_id"])
        cek(f"dropdown prodi untuk jurusan {jurusan[0]['nama_jurusan']} ({len(prodi)} prodi)", len(prodi) >= 1)

    # --- sebagai admin ---
    auth.login_admin(input("Username admin: "), getpass("Password (layar tampak kosong, itu normal): "))
    semua = mahasiswa.daftar()
    cek(f"login admin; daftar mahasiswa terbaca ({len(semua)} orang)", len(semua) >= 1)

    p = nilai.pratinjau(60, 50, 45)
    cek("pratinjau nilai 60/50/45 = 51.00 (D)", float(p["nilai_akhir"]) == 51.0 and p["huruf_mutu"] == "D")

    r = ipk.ipk("2501001")
    if r is None:
        print("[LEWAT] data contoh Budi (2501001) tidak ditemukan; seed.sql mungkin belum diimpor.")
    else:
        cek(f"IPK Budi = 3.36 (hasil: {r['ipk']})", hampir(r["ipk"], 3.36))
        ips = ipk.ips_per_semester("2501001")
        cek(f"IPS Budi = 2.83 dan 3.06 (hasil: {[str(x['ips']) for x in ips]})",
            len(ips) == 2 and hampir(ips[0]["ips"], 2.83) and hampir(ips[1]["ips"], 3.06))
        t = ipk.transkrip("2501001")
        if_101 = [x for x in t if x["kode_mk"] == "IF101"]
        cek("transkrip Budi: 5 mata kuliah, IF101 memakai nilai terbaik (B)",
            len(t) == 5 and if_101 and if_101[0]["huruf_mutu"] == "B")

    print("\nDaftar IPK semua mahasiswa:")
    for x in ipk.daftar_ipk():
        print(f"  {x['nim']:<10} {x['nama_lengkap']:<20} IPK: {x['ipk'] if x['ipk'] is not None else '-'}")
    auth.logout()

    # --- sebagai mahasiswa (login Nama + NIM) ---
    if r is not None:
        auth.login_mahasiswa("Budi Santoso", "2501001")
        cek("login mahasiswa dengan Nama + NIM", True)
        cek("mahasiswa melihat IPK sendiri", hampir(ipk.ipk()["ipk"], 3.36))
        try:
            ipk.ipk("2501002")
            cek("mahasiswa tidak boleh melihat IPK orang lain", False)
        except AksesDitolak:
            cek("mahasiswa tidak boleh melihat IPK orang lain", True)
        try:
            mahasiswa.daftar()
            cek("mahasiswa tidak boleh membuka daftar mahasiswa", False)
        except AksesDitolak:
            cek("mahasiswa tidak boleh membuka daftar mahasiswa", True)
        auth.logout()

    print("\nSelesai.")
except AppError as err:
    print("Berhenti:", err)