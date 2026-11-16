"""Hash dan verifikasi password (bcrypt)."""
import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:  # hash rusak, atau password > 72 byte
        return False


_dummy_hash = None


def dummy_verify(password: str) -> None:
    """Dipanggil saat username tidak ditemukan, supaya waktu respons
    sama dengan username yang ada (mencegah penebakan username)."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = hash_password("dummy-password")
    verify_password(password, _dummy_hash)