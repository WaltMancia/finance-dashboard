from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.infrastructure.database.models import Category


def find_all_for_user(db: Session, user_id: int) -> list[Category]:
    """
    Devuelve las categorías del sistema (is_default=True)
    más las categorías personales del usuario.
    OR en SQLAlchemy se hace con or_()
    """
    return (
        db.query(Category)
        .filter(
            or_(
                Category.is_default == True,
                Category.user_id == user_id,
            )
        )
        .order_by(Category.name)
        .all()
    )


def find_by_id(db: Session, category_id: int, user_id: int) -> Category | None:
    """
    Busca una categoría que pertenezca al usuario o sea del sistema.
    Evita que un usuario acceda a categorías de otro.
    """
    return (
        db.query(Category)
        .filter(
            Category.id == category_id,
            or_(
                Category.is_default == True,
                Category.user_id == user_id,
            ),
        )
        .first()
    )


def create(db: Session, user_id: int, name: str, color: str, icon: str) -> Category:
    category = Category(
        user_id=user_id,
        name=name,
        color=color,
        icon=icon,
        is_default=False,  # Las categorías de usuarios nunca son default
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update(db: Session, category: Category, data: dict) -> Category:
    # Actualizamos solo los campos que vienen en el request
    # exclude_none=True filtra los campos que son None
    for field, value in data.items():
        if value is not None:
            setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()