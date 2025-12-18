from http.client import HTTPException
from backend.utils.regex import PASSWORD_REGEX


def validate_password(password: str) -> None:
    if not PASSWORD_REGEX.match(password):
        raise HTTPException(
            status_code=400,
            detail=(
                "Password must be at least 8 characters long and include "
                "uppercase, lowercase, number, and special character."
            )
        )
