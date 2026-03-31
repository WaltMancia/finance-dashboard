import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.connection import Base, get_db
from app.infrastructure.database.seeds import seed_default_categories
from app.core.config import settings
from main import app

# ── Engine de tests ──────────────────────────────────────────
# Usamos la BD de tests, nunca la de desarrollo
TEST_DATABASE_URL = settings.database_url.replace(
    "finance_db", "finance_test_db"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ── Fixtures de Base de Datos ────────────────────────────────

@pytest.fixture(scope="session")
def setup_database():
    """
    Crea todas las tablas al inicio de la sesión de tests
    y las elimina al final.
    scope="session" → se ejecuta UNA vez para todos los tests.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db(setup_database):
    """
    Provee una sesión de BD limpia para cada test.
    Usa transacciones que se revierten al terminar cada test
    → cada test empieza con la BD vacía.
    scope="function" → se ejecuta una vez POR CADA test.
    """
    connection = test_engine.connect()

    # Iniciamos una transacción que revertiremos al final
    # Esto es mucho más rápido que borrar y recrear tablas
    transaction = connection.begin()

    session = TestSessionLocal(bind=connection)

    # Sembramos las categorías por defecto
    seed_default_categories(session)

    yield session

    # Limpieza: cerramos sesión y revertimos TODOS los cambios del test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """
    Cliente HTTP de prueba que usa la BD de tests.
    Sobreescribe la dependency get_db con la BD de tests.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # La sesión la maneja la fixture db

    # dependency_overrides reemplaza dependencias en tiempo de test
    # Es la forma oficial de FastAPI para mockear dependencias
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Limpiamos los overrides al terminar
    app.dependency_overrides.clear()


# ── Factories de datos ───────────────────────────────────────

@pytest.fixture
def user_data():
    """Datos válidos para crear un usuario."""
    return {
        "name": "Juan Pérez",
        "email": "juan@test.com",
        "password": "password123",
    }


@pytest.fixture
def second_user_data():
    """Segundo usuario para tests de aislamiento."""
    return {
        "name": "María García",
        "email": "maria@test.com",
        "password": "password123",
    }


@pytest.fixture
def registered_user(client, user_data):
    """
    Fixture compuesta: registra un usuario y devuelve sus datos.
    Otros tests que necesiten un usuario registrado usan esta fixture.
    """
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(registered_user):
    """
    Fixture compuesta: devuelve los headers de autenticación.
    Cualquier test que necesite autenticación usa esta fixture.
    """
    token = registered_user["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def transaction_data():
    """Datos válidos para crear una transacción de gasto."""
    return {
        "amount": 150.00,
        "description": "Supermercado test",
        "type": "expense",
        "date": "2024-01-15T10:00:00Z",
        "category_id": None,
    }


@pytest.fixture
def income_data():
    """Datos válidos para crear una transacción de ingreso."""
    return {
        "amount": 3000.00,
        "description": "Salario enero",
        "type": "income",
        "date": "2024-01-01T10:00:00Z",
        "category_id": None,
    }