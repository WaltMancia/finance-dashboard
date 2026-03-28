from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr          # EmailStr valida formato de email automáticamente
    password: str

    # field_validator reemplaza a validator en Pydantic v2
    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    # Schema de respuesta — nunca incluye password_hash
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    # model_config reemplaza a class Config en Pydantic v2
    # from_attributes=True permite crear el schema desde un modelo SQLAlchemy
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"