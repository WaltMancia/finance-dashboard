from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories import user_repository
from app.infrastructure.utils.jwt import decode_token
from app.infrastructure.database.models import User

# HTTPBearer extrae automáticamente el token del header Authorization: Bearer <token>
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency que verifica el token y devuelve el usuario autenticado.
    Si el token es inválido o expirado, FastAPI responde 401 automáticamente.

    Uso en un endpoint:
        def my_endpoint(user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        # WWW-Authenticate es el header estándar de HTTP para auth
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise credentials_exception

        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    user = user_repository.find_by_id(db, user_id)
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency compuesta — reutiliza get_current_user y añade
    verificación de que el usuario esté activo.
    Las dependencies se pueden encadenar así infinitamente.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return current_user