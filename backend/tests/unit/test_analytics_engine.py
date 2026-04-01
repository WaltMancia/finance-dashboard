import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.infrastructure.ml.analytics_engine import AnalyticsEngine


# ── Helpers para crear datos de prueba ──────────────────────

def make_transaction(
    amount: float,
    type: str,
    date: str,
    category_name: str = "Alimentación",
    category_color: str = "#f97316",
    category_icon: str = "🍔",
    category_id: int = 1,
):
    """Fábrica de transacciones para tests."""
    return {
        "id": 1,
        "amount": Decimal(str(amount)),
        "type": type,
        "date": datetime.fromisoformat(date).replace(tzinfo=timezone.utc),
        "description": "Test transaction",
        "category_id": category_id,
        "category_name": category_name,
        "category_color": category_color,
        "category_icon": category_icon,
    }


# ── Tests del resumen general ────────────────────────────────

class TestGetSummary:
    """
    Agrupamos tests relacionados en clases.
    Es más organizado y permite fixtures a nivel de clase.
    """

    def test_empty_transactions_returns_zeros(self):
        """Con lista vacía, todos los valores deben ser 0."""
        engine = AnalyticsEngine([])
        summary = engine.get_summary()

        assert summary["total_income"] == 0
        assert summary["total_expenses"] == 0
        assert summary["balance"] == 0

    def test_calculates_balance_correctly(self):
        """El balance debe ser ingresos - gastos."""
        transactions = [
            make_transaction(3000, "income", "2024-01-01"),
            make_transaction(150, "expense", "2024-01-15"),
            make_transaction(80, "expense", "2024-01-20"),
        ]
        engine = AnalyticsEngine(transactions)
        summary = engine.get_summary()

        assert summary["total_income"] == 3000.0
        assert summary["total_expenses"] == 230.0
        assert summary["balance"] == 2770.0

    def test_only_expenses_gives_negative_balance(self):
        """Si solo hay gastos, el balance debe ser negativo."""
        transactions = [
            make_transaction(500, "expense", "2024-01-10"),
            make_transaction(200, "expense", "2024-01-15"),
        ]
        engine = AnalyticsEngine(transactions)
        summary = engine.get_summary()

        assert summary["total_income"] == 0
        assert summary["total_expenses"] == 700.0
        assert summary["balance"] == -700.0

    def test_transaction_count_is_correct(self):
        """El conteo de transacciones debe ser exacto."""
        transactions = [make_transaction(100, "expense", "2024-01-01")] * 5
        engine = AnalyticsEngine(transactions)

        assert engine.get_summary()["transaction_count"] == 5


# ── Tests del desglose por categoría ────────────────────────

class TestCategoryBreakdown:

    def test_percentages_sum_to_100(self):
        """Los porcentajes de todas las categorías deben sumar 100%."""
        transactions = [
            make_transaction(200, "expense", "2024-01-01", "Alimentación", category_id=1),
            make_transaction(150, "expense", "2024-01-02", "Transporte", category_id=2),
            make_transaction(150, "expense", "2024-01-03", "Entretenimiento", category_id=3),
        ]
        engine = AnalyticsEngine(transactions)
        breakdown = engine.get_category_breakdown()

        total_pct = sum(cat["percentage"] for cat in breakdown)
        # Usamos pytest.approx para comparar floats con tolerancia
        # 99.9% == 100% por redondeo es aceptable
        assert total_pct == pytest.approx(100.0, abs=0.5)

    def test_income_not_included_in_breakdown(self):
        """Los ingresos NO deben aparecer en el desglose de gastos."""
        transactions = [
            make_transaction(3000, "income", "2024-01-01", "Salario"),
            make_transaction(200, "expense", "2024-01-15", "Alimentación"),
        ]
        engine = AnalyticsEngine(transactions)
        breakdown = engine.get_category_breakdown()

        category_names = [c["category_name"] for c in breakdown]
        assert "Salario" not in category_names
        assert "Alimentación" in category_names

    def test_sorted_by_total_descending(self):
        """Las categorías deben ordenarse de mayor a menor gasto."""
        transactions = [
            make_transaction(100, "expense", "2024-01-01", "Pequeño", category_id=1),
            make_transaction(500, "expense", "2024-01-02", "Grande", category_id=2),
            make_transaction(250, "expense", "2024-01-03", "Mediano", category_id=3),
        ]
        engine = AnalyticsEngine(transactions)
        breakdown = engine.get_category_breakdown()

        totals = [cat["total"] for cat in breakdown]
        assert totals == sorted(totals, reverse=True)

    def test_empty_returns_empty_list(self):
        """Sin transacciones, el desglose debe ser una lista vacía."""
        engine = AnalyticsEngine([])
        assert engine.get_category_breakdown() == []


# ── Tests de la tendencia mensual ───────────────────────────

class TestMonthlyTrend:

    def test_groups_by_month_correctly(self):
        """Transacciones del mismo mes deben agruparse."""
        transactions = [
            make_transaction(100, "expense", "2024-01-10"),
            make_transaction(200, "expense", "2024-01-20"),  # mismo mes
            make_transaction(300, "expense", "2024-02-15"),  # mes diferente
        ]
        engine = AnalyticsEngine(transactions)
        trend = engine.get_monthly_trend()

        # Debe haber 2 meses, no 3 filas
        assert len(trend) == 2

        jan = next(m for m in trend if m["month"] == "2024-01")
        assert jan["expenses"] == 300.0  # 100 + 200

    def test_balance_is_income_minus_expenses(self):
        """El balance de cada mes debe ser ingresos - gastos."""
        transactions = [
            make_transaction(3000, "income", "2024-01-01"),
            make_transaction(500, "expense", "2024-01-15"),
        ]
        engine = AnalyticsEngine(transactions)
        trend = engine.get_monthly_trend()

        jan = trend[0]
        assert jan["income"] == 3000.0
        assert jan["expenses"] == 500.0
        assert jan["balance"] == 2500.0

    def test_respects_months_limit(self):
        """El parámetro months debe limitar el número de resultados."""
        transactions = [
            make_transaction(100, "expense", f"2024-0{m}-01")
            for m in range(1, 7)  # 6 meses
        ]
        engine = AnalyticsEngine(transactions)

        assert len(engine.get_monthly_trend(months=3)) <= 3
        assert len(engine.get_monthly_trend(months=6)) <= 6


# ── Tests del CSV Processor ──────────────────────────────────

class TestCSVProcessor:
    """Tests para el procesador de CSV."""

    def test_standard_format(self):
        """Debe procesar correctamente el formato estándar."""
        from app.infrastructure.ml.csv_processor import CSVProcessor

        csv_content = b"""date,description,amount,type
2024-01-15,Supermercado,150.00,expense
2024-01-16,Salario,3000.00,income
2024-01-17,Netflix,15.99,expense
"""
        processor = CSVProcessor(csv_content, "test.csv")
        df = processor.process()

        valid_rows = df[df["is_valid"] == True]
        assert len(valid_rows) == 3

    def test_invalid_rows_marked_correctly(self):
        """Las filas con datos inválidos deben marcarse como inválidas."""
        from app.infrastructure.ml.csv_processor import CSVProcessor

        csv_content = b"""date,description,amount,type
2024-01-15,Valida,150.00,expense
invalid-date,Fecha mala,50.00,expense
2024-01-17,Monto malo,abc,expense
"""
        processor = CSVProcessor(csv_content, "test.csv")
        df = processor.process()

        valid_count = int(df["is_valid"].sum())
        invalid_count = int((~df["is_valid"]).sum())

        assert valid_count == 1
        assert invalid_count == 2

    def test_semicolon_separator(self):
        """Debe detectar punto y coma como separador."""
        from app.infrastructure.ml.csv_processor import CSVProcessor

        csv_content = b"""date;description;amount;type
2024-01-15;Supermercado;150.00;expense
"""
        processor = CSVProcessor(csv_content, "test.csv")
        df = processor.process()

        assert len(df) == 1
        assert df.iloc[0]["is_valid"] == True

    def test_debit_credit_columns(self):
        """Debe manejar columnas separadas de débito y crédito."""
        from app.infrastructure.ml.csv_processor import CSVProcessor

        csv_content = b"""date,description,debit,credit
2024-01-15,Supermercado,150.00,
2024-01-16,Salario,,3000.00
"""
        processor = CSVProcessor(csv_content, "test.csv")
        df = processor.process()

        valid = df[df["is_valid"] == True]
        assert len(valid) == 2

        expense_row = df[df["type"] == "expense"].iloc[0]
        income_row = df[df["type"] == "income"].iloc[0]

        assert float(expense_row["amount"]) == 150.0
        assert float(income_row["amount"]) == 3000.0

    def test_preview_returns_correct_structure(self):
        """El preview debe tener la estructura correcta."""
        from app.infrastructure.ml.csv_processor import CSVProcessor

        csv_content = b"""date,description,amount,type
2024-01-15,Test,100.00,expense
"""
        processor = CSVProcessor(csv_content, "test.csv")
        processor.process()
        preview = processor.get_preview()

        assert "total_rows" in preview
        assert "valid_rows" in preview
        assert "invalid_rows" in preview
        assert "preview" in preview
        assert isinstance(preview["preview"], list)
        assert preview["preview"][0]["category_name"] == "Otros"

    def test_detects_category_from_description(self):
        """La categoría debe inferirse desde la descripción cuando no viene en el CSV."""
        from app.infrastructure.ml.csv_processor import CSVProcessor

        csv_content = b"""date,description,amount,type
2024-01-15,Supermercado del mes,150.00,expense
2024-01-16,Salario enero,3000.00,income
"""
        processor = CSVProcessor(csv_content, "test.csv")
        df = processor.process()

        category_names = list(df["category_name"])
        assert category_names[0] == "Alimentación"
        assert category_names[1] == "Salario"