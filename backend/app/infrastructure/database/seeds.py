from sqlalchemy.orm import Session
from app.infrastructure.database.models import Category


DEFAULT_CATEGORIES = [
    {"name": "Alimentación",   "color": "#f97316", "icon": "🍔", "is_default": True},
    {"name": "Transporte",     "color": "#3b82f6", "icon": "🚗", "is_default": True},
    {"name": "Entretenimiento","color": "#8b5cf6", "icon": "🎬", "is_default": True},
    {"name": "Salud",          "color": "#ef4444", "icon": "💊", "is_default": True},
    {"name": "Educación",      "color": "#10b981", "icon": "📚", "is_default": True},
    {"name": "Ropa",           "color": "#f59e0b", "icon": "👕", "is_default": True},
    {"name": "Hogar",          "color": "#6366f1", "icon": "🏠", "is_default": True},
    {"name": "Servicios",      "color": "#14b8a6", "icon": "💡", "is_default": True},
    {"name": "Salario",        "color": "#22c55e", "icon": "💼", "is_default": True},
    {"name": "Otros",          "color": "#94a3b8", "icon": "📦", "is_default": True},
]

def seed_default_categories(db: Session) -> None:
    """
    Inserta categorías por defecto si no existen.
    Idempotente: se puede llamar múltiples veces sin duplicar datos.
    """
    existing = db.query(Category).filter(Category.is_default == True).count()

    if existing > 0:
        print("✅ Default categories already exist, skipping seed.")
        return

    categories = [Category(**cat) for cat in DEFAULT_CATEGORIES]
    db.add_all(categories)
    db.commit()
    print(f"✅ Seeded {len(categories)} default categories.")