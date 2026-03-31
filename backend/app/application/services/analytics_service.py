from sqlalchemy.orm import Session
from app.infrastructure.repositories import transaction_repository
from app.infrastructure.ml.analytics_engine import AnalyticsEngine


def get_full_analytics(db: Session, user_id: int) -> dict:
    """
    Obtiene todas las transacciones del usuario y las pasa
    al motor de análisis para generar el dashboard completo.
    """
    transactions = transaction_repository.find_all_for_analytics(db, user_id)
    engine = AnalyticsEngine(transactions)
    return engine.get_full_analytics()


def get_monthly_trend(db: Session, user_id: int, months: int = 6) -> list:
    transactions = transaction_repository.find_all_for_analytics(db, user_id)
    engine = AnalyticsEngine(transactions)
    return engine.get_monthly_trend(months=months)


def get_category_breakdown(
    db: Session,
    user_id: int,
    month_key: str | None = None,
) -> list:
    transactions = transaction_repository.find_all_for_analytics(db, user_id)
    engine = AnalyticsEngine(transactions)
    return engine.get_category_breakdown(month_key=month_key)


def get_prediction(db: Session, user_id: int) -> dict:
    transactions = transaction_repository.find_all_for_analytics(db, user_id)
    engine = AnalyticsEngine(transactions)
    return engine.get_prediction()