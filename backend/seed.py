from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.seeds import seed_default_categories
from app.infrastructure.database.demo_seeds import seed_demo_user

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_default_categories(db)
        seed_demo_user(db)
        print("\n🎉 All seeds completed successfully!")
        print("   Demo user: demo@financeai.com / demo1234")
    finally:
        db.close()