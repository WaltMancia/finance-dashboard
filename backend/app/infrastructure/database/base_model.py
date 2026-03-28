from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.connection import Base


class TimeStampMixin:
    """
    Mixin: clase que añade funcionalidad a otras clases por herencia múltiple
    No es un modelo por sí solo, solo añade los campos de timestamps
    """

    # server_default=func.now() → PostgreSQL pone la fecha automáticamente
    # evita depender del reloj de Python, usa el reloj de la BD
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        # onupdate actualiza automáticamente al modificar el registro
        onupdate=func.now(),
        nullable=False,
    )