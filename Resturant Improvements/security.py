import bcrypt
import secrets
import string


def hash_password(password: str) -> str:
    """Hash password with bcrypt (salt included)."""
    pw = password.encode("utf-8")
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
    except Exception:
        return False


def generate_password(length: int = 12) -> str:
    """Generate random alphanumeric password."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
