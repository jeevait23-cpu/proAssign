import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HASH_ITERATIONS = 260_000


def generate_password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${HASH_ITERATIONS}${salt}${digest}"


def check_password_hash(stored_hash, password):
    try:
        algorithm, iterations, salt, expected_digest = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(actual_digest, expected_digest)


@dataclass
class AuthResult:
    ok: bool
    message: str
    user: dict | None = None


class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def register(self, name, email, password):
        name = (name or "").strip()
        email = (email or "").strip().lower()
        password = password or ""

        if len(name) < 2:
            return AuthResult(False, "Please enter your full name.")
        if not EMAIL_PATTERN.match(email):
            return AuthResult(False, "Please enter a valid email address.")
        if len(password) < 8:
            return AuthResult(False, "Password must be at least 8 characters.")
        if self.user_repo.find_by_email(email):
            return AuthResult(False, "An account already exists for this email.")

        user = self.user_repo.create(
            {
                "name": name,
                "email": email,
                "password_hash": generate_password_hash(password),
            }
        )
        return AuthResult(True, "Account created successfully.", user)

    def login(self, email, password):
        email = (email or "").strip().lower()
        password = password or ""
        user = self.user_repo.find_by_email(email)

        if not user or not check_password_hash(user["password_hash"], password):
            return AuthResult(False, "Invalid email or password.")

        self.user_repo.mark_login(email)
        return AuthResult(True, "Welcome back.", user)
