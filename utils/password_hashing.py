from hashlib import blake2b, sha1, md5
import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = b"pseudorandomly_generated_server_secret_key"
AUTH_SIZE = 32


def hash_password(password: str) -> str:
    """
    Generate a secure hash for the given password using blake2b + bcrypt.
    """
    blake_digest = blake2b(password.encode("utf-8"), digest_size=AUTH_SIZE, key=SECRET_KEY).hexdigest()
    bcrypt_hash = bcrypt.hashpw(blake_digest.encode("utf-8"), bcrypt.gensalt())
    return f"new:{bcrypt_hash.decode()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against the stored hash.
    Supports old and new formats.
    """
    if hashed_password.startswith("old:"):
        sha_enc = sha1(plain_password.encode("utf-8")).hexdigest()
        return md5(sha_enc.encode("utf-8")).hexdigest() == hashed_password.replace("old:", "")
    if hashed_password.startswith("new:"):
        stored_hash = hashed_password.replace("new:", "").encode("utf-8")
        blake_digest = blake2b(plain_password.encode("utf-8"), digest_size=AUTH_SIZE, key=SECRET_KEY).hexdigest()
        return bcrypt.checkpw(blake_digest.encode("utf-8"), stored_hash)
    return pwd_context.verify(plain_password, hashed_password)


def hash_password_bcrypt(password: str) -> str:
    """
    Hash password using modern bcrypt (Passlib).
    """
    return pwd_context.hash(password)
