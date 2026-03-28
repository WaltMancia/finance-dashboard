from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.services import auth_service
from app.application.schemas.auth import (
    UserCreate,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    AccessTokenResponse,
    UserResponse,
)
from app.interfaces.dependencies.auth import get_current_active_user
from app.infrastructure.database.models import User

# prefix agrupa todas las rutas bajo /auth
# tags agrupa los endpoints en Swagger
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y devuelve tokens JWT."""
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Inicia sesión y devuelve tokens JWT."""
    return auth_service.login(db, data.email, data.password)


@router.post("/refresh-token", response_model=AccessTokenResponse)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Genera un nuevo access token usando el refresh token."""
    return auth_service.refresh_access_token(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint protegido — devuelve el usuario autenticado.
    get_current_active_user verifica el token automáticamente.
    No necesitas escribir ninguna lógica de verificación aquí.
    """
    return current_user