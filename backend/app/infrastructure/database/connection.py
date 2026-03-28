from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


# DeclarativeBase es la clase madre de todos los modelos
# Todos los modelos heredarán de esta clase Base
class Base(DeclarativeBase):
    pass


# El engine es la conexión real a PostgreSQL
# pool_pre_ping=True verifica la conexión antes de usarla
# Evita errores cuando la conexión lleva tiempo inactiva
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    # En desarrollo podemos ver las queries SQL en consola
    echo=settings.debug,
)

# SessionLocal es la fábrica de sesiones
# Cada petición HTTP tendrá su propia sesión
# autocommit=False → los cambios no se guardan hasta que llames commit()
# autoflush=False  → los cambios no se sincronizan con BD automáticamente
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Función generadora que provee la sesión de BD
# El yield es importante: FastAPI la usa para inyección de dependencias
# Todo lo que está después del yield se ejecuta al terminar la petición
def get_db():
    db = SessionLocal()
    try:
        yield db          # ← aquí FastAPI inyecta la sesión al endpoint
    finally:
        db.close()        # ← siempre cierra la sesión, haya error o no