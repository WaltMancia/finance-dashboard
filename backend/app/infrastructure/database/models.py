from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Text, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.infrastructure.database.connection import Base
from app.infrastructure.database.base_model import TimeStampMixin


# Enum de Python para el tipo de transacción
# SAEnum lo convierte a un tipo ENUM en PostgreSQL
class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    # La contraseña siempre se guarda hasheada, nunca en texto plano
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships — equivale a los associations de Sequelize
    # back_populates crea la relación bidireccional
    # cascade="all, delete-orphan" → si se borra el user, se borran sus datos
    categories: Mapped[list[Category]] = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    csv_imports: Mapped[list[CSVImport]] = relationship(
        "CSVImport",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Category(Base, TimeStampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # nullable=True para categorías del sistema (sin dueño)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Color en formato hex para visualización en gráficas
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")

    # Emoji o nombre de icono para la UI
    icon: Mapped[str] = mapped_column(String(50), default="💰")

    # Las categorías del sistema son visibles para todos
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped[User | None] = relationship("User", back_populates="categories")
    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        back_populates="category",
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Transaction(Base, TimeStampMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        # SET NULL: si se borra la categoría, la transacción queda sin categoría
        # Es mejor que CASCADE (que borraría la transacción) o RESTRICT (que impide borrar la categoría)
    )

    # Numeric en PostgreSQL es exacto para dinero (equivale a DECIMAL en MySQL)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType),
        nullable=False,
    )

    # La fecha de la transacción puede ser diferente a created_at
    # Por ejemplo al importar un CSV con transacciones del mes pasado
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="transactions")
    category: Mapped[Category | None] = relationship(
        "Category",
        back_populates="transactions",
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.type} {self.amount}>"


class CSVImport(Base, TimeStampMixin):
    __tablename__ = "csv_imports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)

    # Cuántas filas se importaron exitosamente
    rows_imported: Mapped[int] = mapped_column(default=0)

    # pending → processing → completed / failed
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Guardamos errores si el CSV tenía filas inválidas
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    user: Mapped[User] = relationship("User", back_populates="csv_imports")

    def __repr__(self) -> str:
        return f"<CSVImport {self.filename} {self.status}>"