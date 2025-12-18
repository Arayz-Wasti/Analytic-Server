from datetime import datetime, timedelta, timezone
import jwt
from backend.utils.settings import get_settings

settings = get_settings()

ALGORITHM = settings.jwt_algorithm
SECRET_KEY = settings.jwt_secret
ACCESS_EXPIRE_MINUTES = settings.jwt_access_expires
REFRESH_EXPIRE_DAYS = settings.jwt_refresh_expires


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta
) -> str:
    now = datetime.now(tz=timezone.utc)

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    return create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str) -> str:
    return create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS)
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
