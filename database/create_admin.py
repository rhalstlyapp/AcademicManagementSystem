"""
create_admin.py : membuat akun admin awal SIAKAD.

Password diketik saat skrip dijalankan (tidak tampil di layar) dan disimpan
sebagai hash bcrypt. Tidak ada password yang tertulis di kode atau repository.

Jalankan dari folder proyek:
    python database/create_admin.py

Prasyarat: schema.sql dan seed.sql sudah dijalankan, dan file .env sudah diisi.
"""
import os
import sys
from getpass import getpass

import bcrypt
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


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
        pw = getpass("Password admin (min. 8 karakter): ")
        if len(pw) < 8:
            print("Password terlalu pendek, minimal 8 karakter.")
            continue
        if len(pw.encode("utf-8")) > 72:
            print("Password terlalu panjang (bcrypt maksimal 72 byte).")
            continue
        if pw != getpass("Ulangi password: "):
            print("Password tidak sama, coba lagi.")
            continue
        return pw


def main():
    username = input("Username admin [admin]: ").strip() or "admin"
    email = input("Email admin [admin@siakad.local]: ").strip() or "admin@siakad.local"
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
        row = cur.fetchone()
        if row is None:
            print("Role 'admin' belum ada. Jalankan seed.sql terlebih dahulu.")
            sys.exit(1)

        cur.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cur.fetchone():
            print("Username atau email tersebut sudah terdaftar. Tidak ada perubahan.")
            sys.exit(1)

        cur.execute(
            "INSERT INTO users (role_id, username, email, password_hash, is_active) "
            "VALUES (%s, %s, %s, %s, TRUE)",
            (row[0], username, email, password_hash),
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