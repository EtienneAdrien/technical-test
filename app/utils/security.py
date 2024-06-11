from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError


def hash_password(password: str):
    ph = PasswordHasher()
    return ph.hash(password)


def check_hash(password: str, hash_: str):
    ph = PasswordHasher()

    try:
        return ph.verify(hash_, password)
    except (VerifyMismatchError, VerificationError):
        return False
