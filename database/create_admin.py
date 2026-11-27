"""
create_admin.py : membuat akun admin awal SIAKAD.

Password diketik dan terlihat di terminal, lalu disimpan sebagai hash bcrypt.
Tidak ada password yang tertulis di kode atau repository.
Mahasiswa tidak memakai skrip ini: mereka mendaftar sendiri lewat aplikasi.

Jalankan dari folder proyek:
    python database/create_admin.py

Prasyarat: tabel users/roles tersedia, role admin sudah dibuat, dan .env sudah diisi.
"""
import os
import sys
from pathlib import Path

import bcrypt
import mysql.connector
from dotenv import load_dotenv

# Baca .env dari folder proyek, apa pun folder tempat skrip dijalankan.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "siakad"),
    )


def ask_password():
    while True:
        pw = input("Password admin (6-20 karakter): ")
        if len(pw) < 6:
            print("Password terlalu pendek, minimal 6 karakter.")
            continue
        if len(pw) > 20:
            print("Password terlalu panjang, maksimal 20 karakter.")
            continue
        if len(pw.encode("utf-8")) > 72:
            print("Password terlalu panjang (bcrypt maksimal 72 byte).")
            continue
        if pw != input("Ulangi password: "):
            print("Password tidak sama, coba lagi.")
            continue
        return pw


def main():
    username = input("Nama/username admin (maks. 50 karakter): ").strip()
    if not username:
        print("Nama/username admin wajib diisi.")
        sys.exit(1)
    if len(username) > 50:
        print("Nama/username admin maksimal 50 karakter.")
        sys.exit(1)

    password = ask_password()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = connect()
    except mysql.connector.Error as err:
        print(f"Gagal terhubung ke database: {err}")
        sys.exit(1)

    try:
        cur = conn.cursor()
        cur.execute("SELECT role_id FROM roles WHERE nama_role = %s", ("admin",))
        role = cur.fetchone()
        if role is None:
            print("Role admin belum tersedia. Pastikan data roles sudah di-seed.")
            sys.exit(1)

        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            print("Username tersebut sudah terdaftar. Tidak ada perubahan.")
            sys.exit(1)

        cur.execute(
            "INSERT INTO users (role_id, username, email, password_hash, is_active) "
            "VALUES (%s, %s, NULL, %s, TRUE)",
            (role[0], username, password_hash),
        )
        conn.commit()
        print(f"Akun admin '{username}' berhasil dibuat.")
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Gagal menyimpan akun: {err}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
