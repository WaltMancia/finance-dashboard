from pydantic import BaseModel
from datetime import datetime


class MonthlySummary(BaseModel):
    """Resumen de un mes específico."""
    month: str              # "2024-01"
    month_label: str        # "Enero 2024"
    income: float
    expenses: float
    balance: float
    transaction_count: int


class CategoryBreakdown(BaseModel):
    """Desglose de gastos por categoría."""
    category_id: int | None
    category_name: str
    category_color: str
    category_icon: str
    total: float
    percentage: float       # % del total de gastos
    transaction_count: int


class DailyExpense(BaseModel):
    """Gasto de un día específico — para gráfica de calendario."""
    date: str
    amount: float
    transaction_count: int


class PredictionData(BaseModel):
    """Predicción de gastos para el mes actual."""
    current_month_spent: float      # Lo gastado hasta hoy
    predicted_total: float          # Predicción del total del mes
    daily_average: float            # Promedio diario actual
    days_elapsed: int               # Días transcurridos en el mes
    days_remaining: int             # Días que quedan en el mes
    trend: str                      # "up", "down", "stable"
    trend_percentage: float         # Cuánto cambia respecto al mes anterior
    confidence: str                 # "high", "medium", "low"
    # Historial de últimos meses para la gráfica de predicción
    historical_months: list[MonthlySummary]


class ComparisonData(BaseModel):
    """Comparativa entre mes actual y mes anterior."""
    current_month: MonthlySummary
    previous_month: MonthlySummary
    expense_change: float           # diferencia en monto
    expense_change_percentage: float # diferencia en %
    income_change: float
    income_change_percentage: float
    # Categorías donde gastaste más este mes
    top_increases: list[CategoryBreakdown]
    # Categorías donde gastaste menos este mes
    top_decreases: list[CategoryBreakdown]


class FullAnalytics(BaseModel):
    """Respuesta completa del dashboard de análisis."""
    summary: dict                           # Balance general
    monthly_trend: list[MonthlySummary]     # Últimos 6 meses
    category_breakdown: list[CategoryBreakdown]
    daily_expenses: list[DailyExpense]
    prediction: PredictionData
    comparison: ComparisonData