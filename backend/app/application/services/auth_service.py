from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.infrastructure.repositories import user_repository
from app.infrastructure.utils.password import verify_password
from app.infrastructure.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.application.schemas.auth import UserCreate, TokenResponse, UserResponse
from jose import JWTError


def _build_token_response(user) -> TokenResponse:
    """
    Función privada (prefijo _) que construye la respuesta con tokens.
    El prefijo _ es la convención de Python para indicar uso interno.
    """
    payload = {"sub": str(user.id), "email": user.email}

    return TokenResponse(
        user=UserResponse.model_validate(user),
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
    )


def register(db: Session, data: UserCreate) -> TokenResponse:
    existing = user_repository.find_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado",
        )

    user = user_repository.create_user(
        db,
        name=data.name,
        email=data.email,
        password=data.password,
    )

    return _build_token_response(user)


def login(db: Session, email: str, password: str) -> TokenResponse:
    user = user_repository.find_by_email(db, email)

    # Mismo mensaje para usuario no encontrado y contraseña incorrecta
    # No le digas al atacante cuál de los dos falló
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    return _build_token_response(user)


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)

        # Verificamos que sea específicamente un refresh token
        # Un access token no debería poder usarse para refrescar
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        user_id = int(payload.get("sub"))
        user = user_repository.find_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
            )

        new_token = create_access_token(
            {"sub": str(user.id), "email": user.email}
        )

        return {"access_token": new_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido",
        )