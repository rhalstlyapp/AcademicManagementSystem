
import os

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


# Membaca konfigurasi dari file .env
load_dotenv()


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Gagal terhubung ke database: {e}")

    return None


if __name__ == "__main__":
    connection = create_connection()

    if connection:
        print("Database berhasil terhubung!")

        connection.close()
        print("Koneksi database ditutup.")
    else:
        print("Koneksi database gagal.")