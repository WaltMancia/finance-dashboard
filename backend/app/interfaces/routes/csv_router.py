from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.application.services import csv_service
from app.application.schemas.csv_import import CSVImportResponse, CSVPreviewResponse
from app.interfaces.dependencies.auth import get_current_active_user
from app.infrastructure.database.models import User
from app.infrastructure.repositories import csv_import_repository

router = APIRouter(prefix="/csv", tags=["CSV Import"])


@router.post("/preview", response_model=CSVPreviewResponse)
async def preview_csv(
    # File(...) → campo obligatorio de tipo archivo
    file: UploadFile = File(..., description="Archivo CSV a previsualizar"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Previsualiza las primeras filas del CSV sin importarlas.
    Úsalo para verificar que el CSV tiene el formato correcto.
    """
    return await csv_service.preview_csv(file)


@router.post("/import")
async def import_csv(
    file: UploadFile = File(...),
    # Form() permite recibir campos de formulario junto al archivo
    category_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Importa todas las transacciones válidas del CSV a la base de datos.
    """
    return await csv_service.import_csv(db, current_user.id, file, category_id)


@router.get("/imports", response_model=list[CSVImportResponse])
def get_import_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Historial de importaciones del usuario."""
    return csv_import_repository.find_all_by_user(db, current_user.id)