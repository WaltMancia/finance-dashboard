from sqlalchemy.orm import Session
from app.infrastructure.database.models import User
from app.infrastructure.utils.password import hash_password


def find_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def find_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()


def create_user(db: Session, name: str, email: str, password: str) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    # refresh actualiza el objeto con los datos que PostgreSQL generó
    # como el id autoincremental y los timestamps
    db.refresh(user)
    return user