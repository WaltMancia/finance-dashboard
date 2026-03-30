import math
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.infrastructure.repositories import transaction_repository
from app.application.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionFilters
)
from app.application.schemas.shared import PaginatedResponse, Pagination


def get_all(db: Session, user_id: int, filters: TransactionFilters):
    transactions, total = transaction_repository.find_all(
        db,
        user_id=user_id,
        page=filters.page,
        limit=filters.limit,
        type=filters.type,
        category_id=filters.category_id,
        search=filters.search,
        date_from=filters.date_from,
        date_to=filters.date_to,
    )

    return PaginatedResponse(
        data=transactions,
        pagination=Pagination(
            total=total,
            page=filters.page,
            limit=filters.limit,
            # math.ceil redondea hacia arriba
            # 21 transacciones con limit 10 = 3 páginas
            total_pages=math.ceil(total / filters.limit) if total > 0 else 1,
        ),
    )


def get_by_id(db: Session, user_id: int, transaction_id: int):
    transaction = transaction_repository.find_by_id(db, transaction_id, user_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaction


def create(db: Session, user_id: int, data: TransactionCreate):
    # model_dump convierte el schema Pydantic a diccionario Python
    return transaction_repository.create(
        db, user_id, data.model_dump()
    )


def update(db: Session, user_id: int, transaction_id: int, data: TransactionUpdate):
    transaction = transaction_repository.find_by_id(db, transaction_id, user_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    return transaction_repository.update(
        db, transaction, data.model_dump(exclude_none=True)
    )


def delete(db: Session, user_id: int, transaction_id: int):
    transaction = transaction_repository.find_by_id(db, transaction_id, user_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    transaction_repository.delete(db, transaction)


def get_summary(db: Session, user_id: int):
    return transaction_repository.get_summary(db, user_id)