import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO
import unicodedata


# Mapeos de nombres de columnas comunes en distintos bancos/apps
# Si el CSV tiene cualquiera de estos nombres, lo normalizamos al nuestro
COLUMN_MAPPINGS = {
    "date": [
        "date", "fecha", "Date", "Fecha", "transaction_date",
        "fecha_transaccion", "Transaction Date", "Fecha Transacción",
        "fecha_movimiento", "movement_date",
    ],
    "description": [
        "description", "descripcion", "descripción", "concept", "concepto",
        "details", "detalles", "merchant", "comercio", "reference",
        "referencia", "narration", "Descripción", "Description",
    ],
    "amount": [
        "amount", "monto", "importe", "value", "valor",
        "Amount", "Monto", "Importe",
    ],
    "category": [
        "category", "categoria", "categoría", "cat", "rubro",
        "Category", "Categoria", "Categoría",
    ],
    "type": [
        "type", "tipo", "transaction_type", "tipo_transaccion",
        "movement_type", "Type", "Tipo",
    ],
    # Algunos bancos tienen columnas separadas para débito y crédito
    "debit": [
        "debit", "débito", "debito", "cargo", "egreso",
        "Debit", "Débito", "Cargo",
    ],
    "credit": [
        "credit", "crédito", "credito", "abono", "ingreso",
        "Credit", "Crédito", "Abono",
    ],
}

# Formatos de fecha que intentamos parsear en orden
DATE_FORMATS = [
    "%Y-%m-%d",       # 2024-01-15       → ISO estándar
    "%d/%m/%Y",       # 15/01/2024       → formato latinoamericano
    "%m/%d/%Y",       # 01/15/2024       → formato americano
    "%d-%m-%Y",       # 15-01-2024
    "%Y/%m/%d",       # 2024/01/15
    "%d %b %Y",       # 15 Jan 2024
    "%b %d %Y",       # Jan 15 2024
    "%d %B %Y",       # 15 January 2024
    "%Y-%m-%dT%H:%M:%S",  # ISO con tiempo
    "%d/%m/%Y %H:%M", # 15/01/2024 10:30
]

CATEGORY_PATTERNS = [
    (
        "Salario",
        ["salario", "nomina", "nómina", "sueldo", "payroll", "salary", "remuneracion", "remuneración", "pago", "deposito", "jubilación", "pensión", "freelance", "cliente"],
    ),
    (
        "Alimentación",
        ["supermercado", "restaurante", "restaurant", "comida", "food", "grocery", "mercado", "uber eats", "rappi", "delivery", "cafe", "coffee", "almuerzo", "desayuno", "lunch", "dinner"],
    ),
    (
        "Transporte",
        ["uber", "taxi", "gasolina", "gasolinera", "metro", "bus", "autobus", "autobús", "parking", "estacionamiento", "peaje", "cabify", "didi", "transporte"],
    ),
    (
        "Entretenimiento",
        ["netflix", "spotify", "disney", "cine", "movie", "pelicula", "película", "concert", "concierto", "game", "juego", "streaming"],
    ),
    (
        "Salud",
        ["farmacia", "medico", "médico", "doctor", "hospital", "clinica", "clínica", "consulta", "gym", "gimnasio", "salud"],
    ),
    (
        "Educación",
        ["curso", "educacion", "educación", "universidad", "colegio", "escuela", "libro", "books", "udemy", "coursera", "estudio", "learning", "mensualidad escolar", "matricula"],
    ),
    (
        "Ropa",
        ["ropa", "clothing", "camisa", "pantalon", "pantalón", "zapato", "shoes", "sneaker", "moda", "fashion", "vestimenta", "outfit", "short", "falda", "sweater", "chaqueta", "abrigo", "dress", "traje", "accesorio", "accesorios"],
    ),
    (
        "Hogar",
        ["hogar", "casa", "alquiler", "renta", "mortgage", "muebles", "furniture", "decoracion", "decoración", "home"],
    ),
    (
        "Servicios",
        ["luz", "agua", "internet", "telefono", "teléfono", "cell", "celular", "electricidad", "gas", "cable", "servicio"],
    ),
]

DEFAULT_CATEGORY_NAME = "Otros"


class CSVProcessor:
    """
    Clase responsable de leer, limpiar y normalizar archivos CSV
    de transacciones financieras de diferentes fuentes/bancos.
    """

    def __init__(self, file_content: bytes, filename: str):
        self.file_content = file_content
        self.filename = filename
        self.df: pd.DataFrame | None = None
        self.errors: list[str] = []

    def _normalize_text(self, value: str | None) -> str:
        if value is None:
            return ""
        normalized = unicodedata.normalize("NFKD", str(value))
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        return normalized.lower().strip()

    def _detect_category_name(self, row: pd.Series) -> str:
        category_value = row.get("category")
        description_value = row.get("description")
        combined_text = " ".join(
            part for part in [str(category_value or ""), str(description_value or "")]
            if part and part.lower() != "nan"
        )
        normalized_text = self._normalize_text(combined_text)

        if not normalized_text:
            return DEFAULT_CATEGORY_NAME

        for category_name, keywords in CATEGORY_PATTERNS:
            normalized_keywords = [self._normalize_text(keyword) for keyword in keywords]
            if any(keyword and keyword in normalized_text for keyword in normalized_keywords):
                return category_name

        return DEFAULT_CATEGORY_NAME

    # ─────────────────────────────────────────────
    # PASO 1: Leer el CSV con detección automática
    # ─────────────────────────────────────────────

    def _detect_separator(self) -> str:
        """
        Detecta automáticamente si el CSV usa coma, punto y coma u otro separador.
        Lee las primeras líneas y cuenta cuál separador aparece más.
        """
        sample = self.file_content[:2000].decode("utf-8", errors="ignore")
        separators = {",": 0, ";": 0, "\t": 0, "|": 0}

        for sep in separators:
            separators[sep] = sample.count(sep)

        # El separador que más aparece es probablemente el correcto
        return max(separators, key=separators.get)

    def _read_csv(self) -> pd.DataFrame:
        """
        Intenta leer el CSV probando distintas configuraciones.
        Los CSVs reales son sucios — necesitamos ser flexibles.
        """
        separator = self._detect_separator()

        # Intentamos distintas codificaciones — los bancos latinoamericanos
        # suelen exportar en latin-1 o cp1252 en vez de utf-8
        encodings = ["utf-8", "latin-1", "cp1252", "utf-8-sig"]

        for encoding in encodings:
            try:
                # skiprows=0 primero, si falla probamos saltando filas iniciales
                for skip in [0, 1, 2, 3]:
                    try:
                        df = pd.read_csv(
                            BytesIO(self.file_content),
                            sep=separator,
                            encoding=encoding,
                            skiprows=skip,
                            # thousands="," maneja números como "1,000.50"
                            thousands=",",
                            # skip_blank_lines ignora líneas vacías
                            skip_blank_lines=True,
                        )

                        # Si tiene al menos 2 columnas y 1 fila, asumimos éxito
                        if len(df.columns) >= 2 and len(df) > 0:
                            return df

                    except Exception:
                        continue

            except Exception:
                continue

        raise ValueError(
            "No se pudo leer el CSV. Verifica el formato del archivo."
        )

    # ─────────────────────────────────────────────
    # PASO 2: Normalizar nombres de columnas
    # ─────────────────────────────────────────────

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renombra las columnas del CSV a nuestros nombres estándar
        usando el mapeo de columnas definido arriba.
        """
        # Limpiamos los nombres: quitamos espacios y ponemos en minúsculas
        df.columns = df.columns.str.strip().str.lower()

        rename_map = {}

        for standard_name, aliases in COLUMN_MAPPINGS.items():
            for alias in aliases:
                if alias.lower() in df.columns:
                    rename_map[alias.lower()] = standard_name
                    break  # Ya encontramos el alias para este campo, seguimos

        df = df.rename(columns=rename_map)
        return df

    # ─────────────────────────────────────────────
    # PASO 3: Manejar columnas de débito/crédito separadas
    # ─────────────────────────────────────────────

    def _handle_debit_credit_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Algunos bancos tienen columnas separadas para débito y crédito:
        | date       | description  | debit  | credit |
        | 15/01/2024 | Supermercado | 150.00 |        |
        | 16/01/2024 | Salario      |        | 3000   |

        Lo convertimos a una sola columna 'amount' con su 'type'.
        """
        has_debit = "debit" in df.columns
        has_credit = "credit" in df.columns
        has_amount = "amount" in df.columns

        if has_debit and has_credit and not has_amount:
            # Convertimos ambas columnas a numérico
            df["debit"] = pd.to_numeric(
                df["debit"].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            ).fillna(0)

            df["credit"] = pd.to_numeric(
                df["credit"].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            ).fillna(0)

            # Combinamos: el amount es el que no es cero
            df["amount"] = df.apply(
                lambda row: row["credit"] if row["credit"] > 0 else row["debit"],
                axis=1,  # axis=1 → aplica la función fila por fila
            )

            # Determinamos el tipo según cuál columna tiene valor
            df["type"] = df.apply(
                lambda row: "income" if row["credit"] > 0 else "expense",
                axis=1,
            )

            df = df.drop(columns=["debit", "credit"])

        return df

    # ─────────────────────────────────────────────
    # PASO 4: Limpiar y convertir tipos de datos
    # ─────────────────────────────────────────────

    def _clean_amount(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia la columna amount de caracteres no numéricos.
        Los bancos pueden exportar: "$150.00", "1.500,00", "-150", "150 USD"
        """
        if "amount" not in df.columns:
            raise ValueError("No se encontró columna de monto en el CSV")

        # Convertimos a string primero para limpiar caracteres
        amount_str = df["amount"].astype(str)

        # Eliminamos símbolos de moneda y espacios
        amount_str = amount_str.str.replace(r"[$€£¥\s]", "", regex=True)

        # Detectamos si usa punto como separador de miles o de decimales
        # "1.500,00" → europeo: punto=miles, coma=decimal
        # "1,500.00" → americano: coma=miles, punto=decimal
        has_comma_decimal = amount_str.str.contains(r"\d,\d{2}$", regex=True).any()

        if has_comma_decimal:
            # Formato europeo: eliminamos punto de miles, reemplazamos coma decimal
            amount_str = amount_str.str.replace(".", "", regex=False)
            amount_str = amount_str.str.replace(",", ".", regex=False)
        else:
            # Formato americano/estándar: solo eliminamos comas de miles
            amount_str = amount_str.str.replace(",", "", regex=False)

        df["amount"] = pd.to_numeric(amount_str, errors="coerce")

        # Los montos negativos en algunos CSVs indican gastos
        # Los guardamos con signo positivo y determinamos el tipo por el signo
        if "type" not in df.columns:
            df["type"] = df["amount"].apply(
                lambda x: "income" if x > 0 else "expense"
            )

        # Hacemos el monto siempre positivo
        df["amount"] = df["amount"].abs()

        return df

    def _clean_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Intenta parsear la fecha con múltiples formatos.
        Si ningún formato funciona, marca la fila como inválida (NaT).
        """
        if "date" not in df.columns:
            raise ValueError("No se encontró columna de fecha en el CSV")

        # Primero intentamos con inferencia automática de Pandas
        df["date"] = pd.to_datetime(df["date"], infer_datetime_format=True, errors="coerce")

        # Para las filas donde falló (NaT), intentamos formato por formato
        mask_nat = df["date"].isna()
        if mask_nat.any():
            for fmt in DATE_FORMATS:
                still_nat = df["date"].isna()
                if not still_nat.any():
                    break
                df.loc[still_nat, "date"] = pd.to_datetime(
                    df.loc[still_nat, "date_original"]
                    if "date_original" in df.columns
                    else df.loc[still_nat, "date"],
                    format=fmt,
                    errors="coerce",
                )

        return df

    def _normalize_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza la columna type a solo 'income' o 'expense'.
        Los CSVs pueden traer 'débito', 'crédito', 'D', 'C', etc.
        """
        if "type" not in df.columns:
            # Si no hay columna type, asumimos todo como gasto
            df["type"] = "expense"
            return df

        type_map = {
            # Inglés
            "income": "income",
            "expense": "expense",
            "credit": "income",
            "debit": "expense",
            "c": "income",
            "d": "expense",
            # Español
            "ingreso": "income",
            "gasto": "expense",
            "crédito": "income",
            "credito": "income",
            "débito": "expense",
            "debito": "expense",
            "abono": "income",
            "cargo": "expense",
        }

        df["type"] = (
            df["type"]
            .astype(str)
            .str.lower()
            .str.strip()
            .map(type_map)
            # Si no mapea a ninguno, lo dejamos como expense por defecto
            .fillna("expense")
        )

        return df

    # ─────────────────────────────────────────────
    # PASO 5: Validar filas y generar reporte
    # ─────────────────────────────────────────────

    def _validate_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Marca cada fila como válida o inválida con su motivo.
        Las filas inválidas no se importarán pero se reportan al usuario.
        """
        df["is_valid"] = True
        df["validation_error"] = None

        # Validación de monto
        invalid_amount = df["amount"].isna() | (df["amount"] <= 0)
        df.loc[invalid_amount, "is_valid"] = False
        df.loc[invalid_amount, "validation_error"] = "Monto inválido o cero"

        # Validación de fecha
        invalid_date = df["date"].isna()
        df.loc[invalid_date & df["is_valid"], "is_valid"] = False
        df.loc[invalid_date & (df["validation_error"].isna()), "validation_error"] = (
            "Fecha inválida o no reconocida"
        )

        return df

    # ─────────────────────────────────────────────
    # API pública del procesador
    # ─────────────────────────────────────────────

    def process(self) -> pd.DataFrame:
        """
        Ejecuta todo el pipeline de procesamiento en orden.
        Devuelve un DataFrame limpio y normalizado.
        """
        # 1. Leer
        df = self._read_csv()

        # Guardamos la fecha original antes de transformar
        if "date" in df.columns or any(
            col.lower() in ["fecha", "date"] for col in df.columns
        ):
            df["date_original"] = df.get("date", df.get("fecha", ""))

        # 2. Normalizar columnas
        df = self._normalize_columns(df)

        # 3. Manejar débito/crédito separados
        df = self._handle_debit_credit_columns(df)

        # 4. Limpiar tipos de datos
        df = self._clean_amount(df)
        df = self._clean_date(df)
        df = self._normalize_type(df)

        # 5. Limpiar description
        if "description" in df.columns:
            df["description"] = df["description"].astype(str).str.strip()
            # Reemplazamos "nan" string por None
            df["description"] = df["description"].replace("nan", None)
        else:
            df["description"] = None

        # 6. Detectar categoría por fila
        df["category_name"] = df.apply(self._detect_category_name, axis=1)

        # 7. Validar
        df = self._validate_rows(df)

        # Guardamos el DataFrame procesado para uso posterior
        self.df = df
        return df

    def get_preview(self, max_rows: int = 10) -> dict:
        """
        Genera una previsualización de las primeras filas procesadas.
        El usuario puede ver qué se importará antes de confirmar.
        """
        if self.df is None:
            self.process()

        df = self.df
        preview_rows = []

        for idx, (_, row) in enumerate(df.head(max_rows).iterrows()):
            preview_rows.append({
                "row_number": idx + 1,
                "date": str(row["date"])[:10] if pd.notna(row["date"]) else "Inválida",
                "description": row.get("description"),
                "amount": float(row["amount"]) if pd.notna(row["amount"]) else 0,
                "type": row["type"],
                "category_name": row.get("category_name") or DEFAULT_CATEGORY_NAME,
                "is_valid": bool(row["is_valid"]),
                "error": row.get("validation_error"),
            })

        valid_count = int(df["is_valid"].sum())

        return {
            "total_rows": len(df),
            "valid_rows": valid_count,
            "invalid_rows": len(df) - valid_count,
            "preview": preview_rows,
        }

    def get_valid_transactions(self) -> list[dict]:
        """
        Devuelve solo las filas válidas como lista de diccionarios
        listos para insertar en la BD.
        """
        if self.df is None:
            self.process()

        valid_df = self.df[self.df["is_valid"] == True]

        transactions = []
        for _, row in valid_df.iterrows():
            transactions.append({
                "amount": Decimal(str(round(float(row["amount"]), 2))),
                "description": row.get("description"),
                "type": row["type"],
                "category_name": row.get("category_name") or DEFAULT_CATEGORY_NAME,
                # Convertimos a datetime con timezone UTC
                "date": row["date"].to_pydatetime().replace(tzinfo=timezone.utc)
                if pd.notna(row["date"])
                else datetime.now(timezone.utc),
            })

        return transactions