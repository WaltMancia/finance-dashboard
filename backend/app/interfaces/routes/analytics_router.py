from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.services import analytics_service
from app.interfaces.dependencies.auth import get_current_active_user
from app.infrastructure.database.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Análisis completo para el dashboard principal.
    Devuelve: resumen, tendencia mensual, categorías, predicción y comparativa.
    """
    return analytics_service.get_full_analytics(db, current_user.id)


@router.get("/monthly-trend")
def get_monthly_trend(
    months: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Tendencia de ingresos y gastos de los últimos N meses."""
    return analytics_service.get_monthly_trend(db, current_user.id, months)


@router.get("/categories")
def get_category_breakdown(
    month: str | None = Query(
        default=None,
        description="Filtrar por mes en formato YYYY-MM. Ej: 2024-01",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Desglose de gastos por categoría."""
    return analytics_service.get_category_breakdown(db, current_user.id, month)


@router.get("/prediction")
def get_prediction(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Predicción de gastos para el mes actual."""
    return analytics_service.get_prediction(db, current_user.id)