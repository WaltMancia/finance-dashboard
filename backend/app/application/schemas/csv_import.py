from pydantic import BaseModel
from datetime import datetime


class CSVImportResponse(BaseModel):
    id: int
    filename: str
    status: str
    rows_imported: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CSVPreviewRow(BaseModel):
    """
    Representa una fila del CSV ya procesada para previsualización.
    Antes de importar definitivamente, el usuario puede ver qué se importará.
    """
    row_number: int
    date: str
    description: str | None
    amount: float
    type: str           # "income" o "expense"
    is_valid: bool
    error: str | None   # Si la fila tiene un problema, lo describimos aquí


class CSVPreviewResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    preview: list[CSVPreviewRow]