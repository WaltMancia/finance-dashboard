from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from app.core.config import settings


def create_access_token(payload: dict[str, Any]) -> str:
    """
    Genera un access token de corta duración.
    El payload contiene datos del usuario (no sensibles).
    """
    data = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    # exp es una clave estándar de JWT para la expiración
    data["exp"] = expire
    data["type"] = "access"

    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(payload: dict[str, Any]) -> str:
    """
    Genera un refresh token de larga duración.
    Solo se usa para obtener nuevos access tokens.
    """
    data = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    data["exp"] = expire
    data["type"] = "refresh"

    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica y verifica un token JWT.
    Lanza JWTError si es inválido o expirado.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError as e:
        raise JWTError(str(e))