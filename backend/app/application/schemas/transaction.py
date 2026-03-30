from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal
from app.infrastructure.database.models import TransactionType
from app.application.schemas.category import CategoryResponse


class TransactionCreate(BaseModel):
    amount: Decimal
    description: str | None = None
    type: TransactionType
    date: datetime
    category_id: int | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    description: str | None = None
    type: TransactionType | None = None
    date: datetime | None = None
    category_id: int | None = None

    @field_validator("amount", mode="before")
    @classmethod
    def amount_must_be_positive(cls, v) -> Decimal | None:
        if v is not None and Decimal(str(v)) <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    description: str | None
    type: TransactionType
    date: datetime
    category: CategoryResponse | None
    created_at: datetime

    model_config = {"from_attributes": True}


# Schema para los filtros del listado — todos opcionales
class TransactionFilters(BaseModel):
    page: int = 1
    limit: int = 20
    type: TransactionType | None = None
    category_id: int | None = None
    search: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None