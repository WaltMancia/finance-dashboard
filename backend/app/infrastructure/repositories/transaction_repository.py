from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, text
from datetime import datetime
from decimal import Decimal
from app.infrastructure.database.models import Transaction, TransactionType


def find_all(
    db: Session,
    user_id: int,
    page: int = 1,
    limit: int = 20,
    type: TransactionType | None = None,
    category_id: int | None = None,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Transaction], int]:
    """
    Devuelve (transacciones, total) para paginación.
    Aplica filtros dinámicamente según los parámetros recibidos.
    """
    query = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        # joinedload precarga la categoría en la misma query
        # evita el problema N+1: sin esto haría 1 query por cada transacción
        .options(joinedload(Transaction.category))
    )

    # Construimos los filtros dinámicamente
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if search:
        # ilike es LIKE case-insensitive — nativo en PostgreSQL
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    # Contamos el total ANTES de aplicar paginación
    total = query.count()

    transactions = (
        query
        .order_by(Transaction.date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return transactions, total


def find_by_id(db: Session, transaction_id: int, user_id: int) -> Transaction | None:
    return (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
        .options(joinedload(Transaction.category))
        .first()
    )


def create(db: Session, user_id: int, data: dict) -> Transaction:
    transaction = Transaction(user_id=user_id, **data)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    # Recargamos con la categoría incluida para el response
    return find_by_id(db, transaction.id, user_id)


def update(db: Session, transaction: Transaction, data: dict) -> Transaction:
    for field, value in data.items():
        if value is not None:
            setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return find_by_id(db, transaction.id, transaction.user_id)


def delete(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()


def get_summary(db: Session, user_id: int) -> dict:
    """
    Calcula el resumen financiero usando agregaciones de PostgreSQL.
    func.sum y func.coalesce son funciones SQL que SQLAlchemy expone.
    coalesce devuelve 0 si sum es NULL (cuando no hay transacciones).
    """
    result = (
        db.query(
            func.coalesce(
                func.sum(Transaction.amount).filter(
                    Transaction.type == TransactionType.income
                ),
                Decimal("0"),
            ).label("total_income"),
            func.coalesce(
                func.sum(Transaction.amount).filter(
                    Transaction.type == TransactionType.expense
                ),
                Decimal("0"),
            ).label("total_expenses"),
        )
        .filter(Transaction.user_id == user_id)
        .first()
    )

    total_income = result.total_income or Decimal("0")
    total_expenses = result.total_expenses or Decimal("0")

    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "balance": float(total_income - total_expenses),
    }

def find_all_for_analytics(db: Session, user_id: int) -> list[dict]:
    """
    Trae todas las transacciones con datos de categoría aplanados.
    Usamos una query SQL directa para máxima eficiencia.
    text() permite escribir SQL puro cuando el ORM no es lo más eficiente.
    """
    query = text("""
        SELECT
            t.id,
            t.amount,
            t.type,
            t.date,
            t.description,
            t.category_id,
            COALESCE(c.name, 'Sin categoría')  AS category_name,
            COALESCE(c.color, '#94a3b8')        AS category_color,
            COALESCE(c.icon, '📦')              AS category_icon
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = :user_id
        ORDER BY t.date DESC
    """)

    rows = db.execute(query, {"user_id": user_id}).fetchall()

    # Convertimos cada Row a dict para que Pandas lo entienda
    return [row._asdict() for row in rows]