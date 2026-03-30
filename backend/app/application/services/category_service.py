from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.infrastructure.repositories import category_repository
from app.application.schemas.category import CategoryCreate, CategoryUpdate


def get_all(db: Session, user_id: int):
    return category_repository.find_all_for_user(db, user_id)


def create(db: Session, user_id: int, data: CategoryCreate):
    return category_repository.create(
        db,
        user_id=user_id,
        name=data.name,
        color=data.color,
        icon=data.icon,
    )


def update(db: Session, user_id: int, category_id: int, data: CategoryUpdate):
    category = category_repository.find_by_id(db, category_id, user_id)

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Las categorías del sistema no se pueden modificar
    if category.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar categorías del sistema",
        )

    # model_dump(exclude_none=True) convierte el schema a dict
    # excluyendo los campos que son None (no fueron enviados)
    return category_repository.update(
        db, category, data.model_dump(exclude_none=True)
    )


def delete(db: Session, user_id: int, category_id: int):
    category = category_repository.find_by_id(db, category_id, user_id)

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    if category.is_default:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar categorías del sistema",
        )

    category_repository.delete(db, category)