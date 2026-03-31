from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.infrastructure.ml.csv_processor import CSVProcessor
from app.infrastructure.repositories import csv_import_repository, transaction_repository


# Límite de tamaño del archivo: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


async def preview_csv(file: UploadFile) -> dict:
    """
    Lee el CSV y devuelve una previsualización sin guardar nada en la BD.
    El usuario puede revisar qué se va a importar antes de confirmar.
    """
    _validate_file(file)

    content = await file.read()
    _validate_size(content)

    try:
        processor = CSVProcessor(content, file.filename)
        processor.process()
        return processor.get_preview(max_rows=20)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


async def import_csv(
    db: Session,
    user_id: int,
    file: UploadFile,
    category_id: int | None = None,
) -> dict:
    """
    Procesa e importa todas las filas válidas del CSV a la BD.
    Registra el historial de importación en csv_imports.
    """
    _validate_file(file)

    content = await file.read()
    _validate_size(content)

    # Creamos el registro de importación con status "processing"
    csv_import = csv_import_repository.create(db, user_id, file.filename)

    try:
        processor = CSVProcessor(content, file.filename)
        processor.process()

        valid_transactions = processor.get_valid_transactions()

        if not valid_transactions:
            csv_import_repository.update_status(
                db, csv_import, "failed",
                error_message="No se encontraron transacciones válidas en el CSV",
            )
            raise HTTPException(
                status_code=422,
                detail="No se encontraron transacciones válidas en el CSV",
            )

        # Insertamos todas las transacciones válidas
        imported_count = 0
        for transaction_data in valid_transactions:
            if category_id:
                transaction_data["category_id"] = category_id

            transaction_repository.create(db, user_id, transaction_data)
            imported_count += 1

        # Actualizamos el registro como completado
        csv_import_repository.update_status(
            db, csv_import, "completed",
            rows_imported=imported_count,
        )

        preview = processor.get_preview()

        return {
            "message": f"Se importaron {imported_count} transacciones exitosamente",
            "rows_imported": imported_count,
            "rows_skipped": preview["invalid_rows"],
            "import_id": csv_import.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        # Si algo falla, marcamos la importación como fallida
        csv_import_repository.update_status(
            db, csv_import, "failed",
            error_message=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el CSV: {str(e)}",
        )


def _validate_file(file: UploadFile) -> None:
    """Valida que el archivo sea un CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos CSV",
        )


def _validate_size(content: bytes) -> None:
    """Valida que el archivo no supere el límite de tamaño."""
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el límite de {MAX_FILE_SIZE // 1024 // 1024}MB",
        )