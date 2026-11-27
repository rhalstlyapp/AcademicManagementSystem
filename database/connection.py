"""Koneksi MySQL dan fungsi bantu query.

Semua query WAJIB berparameter (%s), jangan pernah memakai f-string:
    fetch_one("SELECT * FROM mahasiswa WHERE nim = %s", (nim,))
"""
from contextlib import contextmanager

import mysql.connector

from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@contextmanager
def db_cursor(commit=False):
    """Buka koneksi + cursor (hasil berupa dict), tutup otomatis.
    Jika terjadi error, transaksi di-rollback."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def fetch_one(sql, params=()):
    with db_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql, params=()):
    with db_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def execute(sql, params=()):
    """INSERT / UPDATE / DELETE. Mengembalikan lastrowid (untuk INSERT)."""
    with db_cursor(commit=True) as cur:
        cur.execute(sql, params)
        return cur.lastrowid