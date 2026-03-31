from sqlalchemy.orm import Session
from app.infrastructure.database.models import CSVImport


def create(db: Session, user_id: int, filename: str) -> CSVImport:
    csv_import = CSVImport(
        user_id=user_id,
        filename=filename,
        status="processing",
    )
    db.add(csv_import)
    db.commit()
    db.refresh(csv_import)
    return csv_import


def update_status(
    db: Session,
    csv_import: CSVImport,
    status: str,
    rows_imported: int = 0,
    error_message: str | None = None,
) -> CSVImport:
    csv_import.status = status
    csv_import.rows_imported = rows_imported
    csv_import.error_message = error_message
    db.commit()
    db.refresh(csv_import)
    return csv_import


def find_all_by_user(db: Session, user_id: int) -> list[CSVImport]:
    return (
        db.query(CSVImport)
        .filter(CSVImport.user_id == user_id)
        .order_by(CSVImport.created_at.desc())
        .all()
    )