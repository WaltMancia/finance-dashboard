import pandas as pd
import numpy as np
from datetime import datetime, timezone
from calendar import monthrange


class AnalyticsEngine:
    """
    Motor de análisis financiero.
    Recibe una lista de transacciones y produce métricas,
    visualizaciones y predicciones.
    """

    def __init__(self, transactions: list[dict]):
        """
        transactions: lista de dicts con keys:
          id, amount, type, date, category_id,
          category_name, category_color, category_icon
        """
        if not transactions:
            self.df = pd.DataFrame()
            self.is_empty = True
            return

        self.df = pd.DataFrame(transactions)
        self.is_empty = False
        self._prepare_dataframe()

    def _prepare_dataframe(self) -> None:
        """
        Prepara el DataFrame para análisis:
        convierte tipos, extrae componentes de fecha.
        """
        # Convertimos amount a float (viene como Decimal de PostgreSQL)
        self.df["amount"] = self.df["amount"].astype(float)

        # Convertimos date a datetime de Pandas
        self.df["date"] = pd.to_datetime(self.df["date"], utc=True)

        # Extraemos componentes de fecha — muy útiles para agrupar
        self.df["year"] = self.df["date"].dt.year
        self.df["month"] = self.df["date"].dt.month
        self.df["day"] = self.df["date"].dt.day

        # Creamos una clave de mes como string "2024-01"
        # zfill(2) rellena con ceros: mes 1 → "01"
        self.df["month_key"] = (
            self.df["year"].astype(str)
            + "-"
            + self.df["month"].astype(str).str.zfill(2)
        )

        # Separamos ingresos y gastos para facilitar los análisis
        self.expenses_df = self.df[self.df["type"] == "expense"].copy()
        self.income_df = self.df[self.df["type"] == "income"].copy()

    # ─────────────────────────────────────────────
    # RESUMEN GENERAL
    # ─────────────────────────────────────────────

    def get_summary(self) -> dict:
        """Balance total: ingresos, gastos y saldo."""
        if self.is_empty:
            return {"total_income": 0, "total_expenses": 0, "balance": 0}

        total_income = float(self.income_df["amount"].sum())
        total_expenses = float(self.expenses_df["amount"].sum())

        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "balance": round(total_income - total_expenses, 2),
            "transaction_count": len(self.df),
        }

    # ─────────────────────────────────────────────
    # TENDENCIA MENSUAL
    # ─────────────────────────────────────────────

    def get_monthly_trend(self, months: int = 6) -> list[dict]:
        """
        Devuelve el resumen de los últimos N meses.
        Usa resample para agrupar por mes eficientemente.
        """
        if self.is_empty:
            return []

        # Nombres de meses en español
        month_names = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
            5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
        }

        # Agrupamos por month_key y tipo de transacción
        grouped = (
            self.df.groupby(["month_key", "year", "month", "type"])["amount"]
            .sum()
            .reset_index()  # Convierte el índice jerárquico en columnas normales
        )

        # Pivotamos para tener income y expense como columnas separadas
        # pivot_table es como una tabla dinámica de Excel
        pivot = grouped.pivot_table(
            index=["month_key", "year", "month"],
            columns="type",
            values="amount",
            fill_value=0,  # Si no hay transacciones de ese tipo, pone 0
        ).reset_index()

        # Aseguramos que existan ambas columnas aunque no haya datos
        if "income" not in pivot.columns:
            pivot["income"] = 0.0
        if "expense" not in pivot.columns:
            pivot["expense"] = 0.0

        # Contamos transacciones por mes
        count_by_month = (
            self.df.groupby("month_key")
            .size()  # size() cuenta filas
            .reset_index(name="transaction_count")
        )

        pivot = pivot.merge(count_by_month, on="month_key", how="left")

        # Ordenamos y tomamos los últimos N meses
        pivot = pivot.sort_values("month_key").tail(months)

        result = []
        for _, row in pivot.iterrows():
            income = round(float(row["income"]), 2)
            expense = round(float(row["expense"]), 2)
            result.append({
                "month": row["month_key"],
                "month_label": f"{month_names[int(row['month'])]} {int(row['year'])}",
                "income": income,
                "expenses": expense,
                "balance": round(income - expense, 2),
                "transaction_count": int(row.get("transaction_count", 0)),
            })

        return result

    # ─────────────────────────────────────────────
    # DESGLOSE POR CATEGORÍA
    # ─────────────────────────────────────────────

    def get_category_breakdown(
        self,
        month_key: str | None = None
    ) -> list[dict]:
        """
        Desglose de gastos por categoría.
        Si se pasa month_key, filtra solo ese mes.
        """
        if self.is_empty:
            return []

        df = self.expenses_df.copy()

        if month_key:
            df = df[df["month_key"] == month_key]

        if df.empty:
            return []

        # Agrupamos por categoría con múltiples métricas a la vez
        grouped = (
            df.groupby(
                ["category_id", "category_name", "category_color", "category_icon"],
                # dropna=False incluye transacciones sin categoría
                dropna=False,
            )
            .agg(
                total=("amount", "sum"),
                count=("amount", "count"),
            )
            .reset_index()
        )

        total_expenses = grouped["total"].sum()

        # Calculamos el porcentaje de cada categoría
        grouped["percentage"] = (
            (grouped["total"] / total_expenses * 100)
            .round(1)
        )

        # Ordenamos de mayor a menor gasto
        grouped = grouped.sort_values("total", ascending=False)

        result = []
        for _, row in grouped.iterrows():
            result.append({
                "category_id": (
                    int(row["category_id"])
                    if pd.notna(row["category_id"])
                    else None
                ),
                "category_name": row["category_name"] or "Sin categoría",
                "category_color": row["category_color"] or "#94a3b8",
                "category_icon": row["category_icon"] or "📦",
                "total": round(float(row["total"]), 2),
                "percentage": float(row["percentage"]),
                "transaction_count": int(row["count"]),
            })

        return result

    # ─────────────────────────────────────────────
    # GASTOS DIARIOS
    # ─────────────────────────────────────────────

    def get_daily_expenses(self, month_key: str | None = None) -> list[dict]:
        """
        Gastos por día — para gráfica de barras o calendario.
        """
        if self.is_empty:
            return []

        df = self.expenses_df.copy()

        if month_key:
            df = df[df["month_key"] == month_key]

        if df.empty:
            return []

        # Agrupamos por fecha exacta
        daily = (
            df.groupby(df["date"].dt.date)
            .agg(
                amount=("amount", "sum"),
                transaction_count=("amount", "count"),
            )
            .reset_index()
        )

        daily = daily.sort_values("date")

        return [
            {
                "date": str(row["date"]),
                "amount": round(float(row["amount"]), 2),
                "transaction_count": int(row["transaction_count"]),
            }
            for _, row in daily.iterrows()
        ]

    # ─────────────────────────────────────────────
    # PREDICCIÓN
    # ─────────────────────────────────────────────

    def get_prediction(self) -> dict:
        """
        Predice el gasto total del mes actual basándose en:
        1. El gasto diario promedio de este mes
        2. La tendencia histórica de los últimos meses
        """
        now = datetime.now(timezone.utc)
        current_month_key = f"{now.year}-{str(now.month).zfill(2)}"

        # Días totales del mes actual y días transcurridos
        days_in_month = monthrange(now.year, now.month)[1]
        days_elapsed = now.day
        days_remaining = days_in_month - days_elapsed

        # ── Gastos del mes actual ──
        current_month_expenses = self.expenses_df[
            self.expenses_df["month_key"] == current_month_key
        ]
        current_spent = float(current_month_expenses["amount"].sum())
        daily_average = current_spent / days_elapsed if days_elapsed > 0 else 0

        # Predicción simple: promedio diario × días totales del mes
        simple_prediction = daily_average * days_in_month

        # ── Predicción con tendencia histórica ──
        # Obtenemos gastos mensuales de los últimos 6 meses
        monthly_data = (
            self.expenses_df
            .groupby("month_key")["amount"]
            .sum()
            .sort_index()
            .tail(6)
        )

        if len(monthly_data) >= 2:
            # Usamos regresión lineal con NumPy para detectar la tendencia
            # x = índices de los meses [0, 1, 2, 3, 4, 5]
            # y = gastos de cada mes
            x = np.arange(len(monthly_data))
            y = monthly_data.values.astype(float)

            # polyfit grado 1 = línea recta = regresión lineal
            # Devuelve [pendiente, intercepto]
            coefficients = np.polyfit(x, y, deg=1)
            slope = coefficients[0]       # cuánto cambia por mes
            intercept = coefficients[1]   # valor inicial

            # Predecimos el siguiente mes (índice len(monthly_data))
            trend_prediction = slope * len(monthly_data) + intercept
            trend_prediction = max(0, float(trend_prediction))  # no puede ser negativo

            # Combinamos ambas predicciones: 70% tendencia, 30% promedio diario
            # Damos más peso a la tendencia si tenemos suficiente historial
            if len(monthly_data) >= 4:
                final_prediction = 0.7 * trend_prediction + 0.3 * simple_prediction
                confidence = "high"
            else:
                final_prediction = 0.5 * trend_prediction + 0.5 * simple_prediction
                confidence = "medium"

            # ── Tendencia: comparamos con el mes anterior ──
            if len(monthly_data) >= 2:
                prev_month_expense = float(monthly_data.iloc[-2])
                if prev_month_expense > 0:
                    trend_pct = ((current_spent - prev_month_expense) / prev_month_expense) * 100
                else:
                    trend_pct = 0.0

                if trend_pct > 5:
                    trend = "up"
                elif trend_pct < -5:
                    trend = "down"
                else:
                    trend = "stable"
            else:
                trend_pct = 0.0
                trend = "stable"

        else:
            # Sin suficiente historial, usamos solo el promedio diario
            final_prediction = simple_prediction
            confidence = "low"
            trend = "stable"
            trend_pct = 0.0

        # ── Historial para la gráfica ──
        historical = self.get_monthly_trend(months=6)

        return {
            "current_month_spent": round(current_spent, 2),
            "predicted_total": round(final_prediction, 2),
            "daily_average": round(daily_average, 2),
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "trend": trend,
            "trend_percentage": round(abs(trend_pct), 1),
            "confidence": confidence,
            "historical_months": historical,
        }

    # ─────────────────────────────────────────────
    # COMPARATIVA MES ACTUAL VS ANTERIOR
    # ─────────────────────────────────────────────

    def get_comparison(self) -> dict:
        """
        Compara el mes actual con el mes anterior.
        Identifica en qué categorías subieron o bajaron los gastos.
        """
        now = datetime.now(timezone.utc)

        # Calculamos la clave del mes anterior
        if now.month == 1:
            prev_year = now.year - 1
            prev_month = 12
        else:
            prev_year = now.year
            prev_month = now.month - 1

        current_key = f"{now.year}-{str(now.month).zfill(2)}"
        prev_key = f"{prev_year}-{str(prev_month).zfill(2)}"

        def get_month_summary(month_key: str) -> dict:
            month_data = self.df[self.df["month_key"] == month_key]
            income = float(month_data[month_data["type"] == "income"]["amount"].sum())
            expenses = float(month_data[month_data["type"] == "expense"]["amount"].sum())
            return {
                "month": month_key,
                "month_label": month_key,
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "balance": round(income - expenses, 2),
                "transaction_count": len(month_data),
            }

        current = get_month_summary(current_key)
        previous = get_month_summary(prev_key)

        # ── Cambio porcentual ──
        def pct_change(current_val: float, prev_val: float) -> float:
            if prev_val == 0:
                return 100.0 if current_val > 0 else 0.0
            return round(((current_val - prev_val) / prev_val) * 100, 1)

        expense_change = current["expenses"] - previous["expenses"]
        income_change = current["income"] - previous["income"]

        # ── Comparativa por categoría ──
        current_cats = {
            c["category_name"]: c
            for c in self.get_category_breakdown(current_key)
        }
        prev_cats = {
            c["category_name"]: c
            for c in self.get_category_breakdown(prev_key)
        }

        # Calculamos el cambio por categoría
        all_categories = set(current_cats.keys()) | set(prev_cats.keys())
        category_changes = []

        for cat_name in all_categories:
            curr_total = current_cats.get(cat_name, {}).get("total", 0)
            prev_total = prev_cats.get(cat_name, {}).get("total", 0)
            change = curr_total - prev_total
            category_changes.append({
                **(current_cats.get(cat_name) or prev_cats.get(cat_name)),
                "total": curr_total,
                "change": change,
            })

        # Ordenamos para identificar mayores aumentos y disminuciones
        increases = sorted(
            [c for c in category_changes if c["change"] > 0],
            key=lambda x: x["change"],
            reverse=True,
        )[:3]  # Top 3 aumentos

        decreases = sorted(
            [c for c in category_changes if c["change"] < 0],
            key=lambda x: x["change"],
        )[:3]  # Top 3 disminuciones

        return {
            "current_month": current,
            "previous_month": previous,
            "expense_change": round(expense_change, 2),
            "expense_change_percentage": pct_change(
                current["expenses"], previous["expenses"]
            ),
            "income_change": round(income_change, 2),
            "income_change_percentage": pct_change(
                current["income"], previous["income"]
            ),
            "top_increases": increases,
            "top_decreases": decreases,
        }

    # ─────────────────────────────────────────────
    # ANÁLISIS COMPLETO — Un solo endpoint
    # ─────────────────────────────────────────────

    def get_full_analytics(self) -> dict:
        """
        Ejecuta todos los análisis y los devuelve juntos.
        El frontend lo llama una sola vez para cargar el dashboard.
        """
        return {
            "summary": self.get_summary(),
            "monthly_trend": self.get_monthly_trend(months=6),
            "category_breakdown": self.get_category_breakdown(),
            "daily_expenses": self.get_daily_expenses(),
            "prediction": self.get_prediction(),
            "comparison": self.get_comparison(),
        }