from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.infrastructure.database.connection import get_db
from app.application.services import transaction_service
from app.application.schemas.transaction import (
    TransactionCreate, TransactionUpdate,
    TransactionResponse, TransactionFilters
)
from app.application.schemas.shared import PaginatedResponse
from app.interfaces.dependencies.auth import get_current_active_user
from app.infrastructure.database.models import User, TransactionType

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=PaginatedResponse[TransactionResponse])
def get_transactions(
    # Query() declara explícitamente que son query params con validación
    page: int = Query(default=1, ge=1),             # ge=1 → mayor o igual a 1
    limit: int = Query(default=20, ge=1, le=100),   # entre 1 y 100
    type: TransactionType | None = Query(default=None),
    category_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    filters = TransactionFilters(
        page=page, limit=limit, type=type,
        category_id=category_id, search=search,
        date_from=date_from, date_to=date_to,
    )
    return transaction_service.get_all(db, current_user.id, filters)


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Devuelve balance total, ingresos y gastos del usuario."""
    return transaction_service.get_summary(db, current_user.id)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return transaction_service.get_by_id(db, current_user.id, transaction_id)


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return transaction_service.create(db, current_user.id, data)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return transaction_service.update(db, current_user.id, transaction_id, data)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    transaction_service.delete(db, current_user.id, transaction_id)