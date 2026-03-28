from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.seeds import seed_default_categories


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()