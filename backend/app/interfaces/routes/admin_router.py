from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.infrastructure.database.connection import get_db, engine
from app.infrastructure.database.models import Transaction, CSVImport
from app.infrastructure.database.seeds import seed_default_categories
from app.infrastructure.database.demo_seeds import seed_demo_user
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/reset-demo")
def reset_demo_data(
    x_reset_secret: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Resetea todos los datos de usuarios y transacciones.
    Mantiene las categorías del sistema.
    Vuelve a crear el usuario demo.
    Solo accesible con la clave secreta en el header.
    """
    if x_reset_secret != settings.reset_secret:
        raise HTTPException(status_code=403, detail="Clave inválida")

    # Borramos en orden correcto para respetar las FK
    db.query(CSVImport).delete()
    db.query(Transaction).delete()

    # Borramos usuarios (cascade borra sus categorías personales)
    from app.infrastructure.database.models import User
    db.query(User).delete()

    db.commit()

    # Recreamos el usuario demo con sus transacciones
    seed_demo_user(db)

    return {
        "message": "Demo data reset successfully",
        "demo_user": "demo@financeai.com",
        "demo_password": "demo1234",
    }