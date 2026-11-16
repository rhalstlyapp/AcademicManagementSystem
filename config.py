"""Konfigurasi aplikasi. Nilai dibaca dari file .env (jangan commit .env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Baca .env dari folder proyek, apa pun folder tempat program dijalankan.
load_dotenv(Path(__file__).resolve().parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "siakad"),
    "charset": "utf8mb4",
    "connection_timeout": 10,
}

SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))