from pydantic import BaseModel, field_validator
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"
    icon: str = "📦"

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        # Validación de formato hex: debe ser #RRGGBB
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("El color debe ser un hex válido (#RRGGBB)")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    icon: str
    is_default: bool
    user_id: int | None

    model_config = {"from_attributes": True}