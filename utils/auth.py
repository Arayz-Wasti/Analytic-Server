from http.client import HTTPException
from time import time
from typing import Any, Dict, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, status
import jwt
from backend.utils.settings import Settings

SECRET_KEY = Settings.jwt_secret
ALGORITHM = Settings.jwt_algorithm

def decode_jwt(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if "sub" not in payload or "type" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    if payload["type"] != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )

    return payload


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, fetch_user: bool = False):
        super().__init__(auto_error=auto_error)
        self.fetch_user = fetch_user

    async def __call__(self, request: Request) -> Dict[str, Any]:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if credentials is None or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_jwt(credentials.credentials)
        if self.fetch_user:
            return payload
        return payload
