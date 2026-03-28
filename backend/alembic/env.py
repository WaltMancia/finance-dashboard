from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Añadimos el directorio backend al path de Python
# Para que Alembic pueda importar nuestros módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.infrastructure.database.connection import Base

# Importamos los modelos para que Alembic los detecte
# Si no los importamos aquí, Alembic no sabe que existen
from app.infrastructure.database.models import (
    User, Category, Transaction, CSVImport
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Le decimos a Alembic cuál es el metadata de nuestros modelos
# Aquí es donde Alembic lee la estructura actual de tus modelos
target_metadata = Base.metadata

# Sobreescribimos la URL de conexión con la de nuestro .env
# Así no tenemos la URL hardcodeada en alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()