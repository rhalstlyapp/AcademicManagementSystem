"""Uji manual login/logout tanpa GUI. Hapus file ini bila sudah tidak diperlukan.
Jalankan dari folder proyek:  python test_auth.py"""
from getpass import getpass

from backend import auth
from utils import session

username = input("Username: ")
password = getpass("Password: ")

try:
    user = auth.login(username, password)
    print("Login berhasil:", user["nama"], "| role:", user["role"])
    print("Sesi aktif   :", session.is_logged_in())
    auth.logout()
    print("Setelah logout, sesi aktif:", session.is_logged_in())
except auth.AuthError as err:
    print("Login gagal:", err)