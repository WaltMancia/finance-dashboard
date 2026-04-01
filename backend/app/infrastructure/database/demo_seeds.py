from datetime import datetime, timezone, timedelta
from decimal import Decimal
import random
from sqlalchemy.orm import Session
from app.infrastructure.database.models import User, Transaction, Category, TransactionType
from app.infrastructure.utils.password import hash_password


# Transacciones realistas con sus categorías
DEMO_TRANSACTIONS = [
    # Enero
    {"desc": "Salario enero",        "amount": 3500, "type": "income",  "cat": "Salario",          "days_ago": 85},
    {"desc": "Supermercado",         "amount": 120,  "type": "expense", "cat": "Alimentación",     "days_ago": 83},
    {"desc": "Restaurante familiar", "amount": 45,   "type": "expense", "cat": "Alimentación",     "days_ago": 80},
    {"desc": "Gasolina",             "amount": 60,   "type": "expense", "cat": "Transporte",       "days_ago": 79},
    {"desc": "Netflix",              "amount": 16,   "type": "expense", "cat": "Entretenimiento",  "days_ago": 78},
    {"desc": "Farmacia",             "amount": 35,   "type": "expense", "cat": "Salud",            "days_ago": 75},
    {"desc": "Luz y agua",           "amount": 80,   "type": "expense", "cat": "Servicios",        "days_ago": 72},
    {"desc": "Cine",                 "amount": 25,   "type": "expense", "cat": "Entretenimiento",  "days_ago": 70},
    {"desc": "Ropa deportiva",       "amount": 90,   "type": "expense", "cat": "Ropa",             "days_ago": 68},
    {"desc": "Supermercado",         "amount": 95,   "type": "expense", "cat": "Alimentación",     "days_ago": 65},
    # Febrero
    {"desc": "Salario febrero",      "amount": 3500, "type": "income",  "cat": "Salario",          "days_ago": 55},
    {"desc": "Supermercado",         "amount": 130,  "type": "expense", "cat": "Alimentación",     "days_ago": 53},
    {"desc": "Uber",                 "amount": 22,   "type": "expense", "cat": "Transporte",       "days_ago": 50},
    {"desc": "Spotify",              "amount": 10,   "type": "expense", "cat": "Entretenimiento",  "days_ago": 48},
    {"desc": "Gym mensualidad",      "amount": 45,   "type": "expense", "cat": "Salud",            "days_ago": 46},
    {"desc": "Internet",             "amount": 50,   "type": "expense", "cat": "Servicios",        "days_ago": 44},
    {"desc": "Freelance proyecto",   "amount": 800,  "type": "income",  "cat": "Otros",            "days_ago": 42},
    {"desc": "Libros técnicos",      "amount": 55,   "type": "expense", "cat": "Educación",        "days_ago": 40},
    {"desc": "Supermercado",         "amount": 110,  "type": "expense", "cat": "Alimentación",     "days_ago": 37},
    {"desc": "Gasolina",             "amount": 65,   "type": "expense", "cat": "Transporte",       "days_ago": 35},
    # Marzo
    {"desc": "Salario marzo",        "amount": 3500, "type": "income",  "cat": "Salario",          "days_ago": 25},
    {"desc": "Supermercado",         "amount": 140,  "type": "expense", "cat": "Alimentación",     "days_ago": 23},
    {"desc": "Restaurante",          "amount": 38,   "type": "expense", "cat": "Alimentación",     "days_ago": 21},
    {"desc": "Netflix",              "amount": 16,   "type": "expense", "cat": "Entretenimiento",  "days_ago": 20},
    {"desc": "Médico consulta",      "amount": 70,   "type": "expense", "cat": "Salud",            "days_ago": 18},
    {"desc": "Ropa casual",          "amount": 75,   "type": "expense", "cat": "Ropa",             "days_ago": 16},
    {"desc": "Luz y agua",           "amount": 85,   "type": "expense", "cat": "Servicios",        "days_ago": 14},
    {"desc": "Curso online",         "amount": 40,   "type": "expense", "cat": "Educación",        "days_ago": 12},
    {"desc": "Uber Eats",            "amount": 28,   "type": "expense", "cat": "Alimentación",     "days_ago": 10},
    {"desc": "Gasolina",             "amount": 58,   "type": "expense", "cat": "Transporte",       "days_ago": 8},
    {"desc": "Freelance logo",       "amount": 350,  "type": "income",  "cat": "Otros",            "days_ago": 6},
    {"desc": "Supermercado",         "amount": 105,  "type": "expense", "cat": "Alimentación",     "days_ago": 4},
    {"desc": "Cine IMAX",            "amount": 30,   "type": "expense", "cat": "Entretenimiento",  "days_ago": 2},
]


def seed_demo_user(db: Session) -> None:
    """
    Crea un usuario de demo con transacciones realistas de 3 meses.
    Idempotente: no crea el usuario si ya existe.
    """
    demo_email = "demo@financeai.com"

    existing = db.query(User).filter(User.email == demo_email).first()
    if existing:
        print("✅ Demo user already exists, skipping.")
        return

    # Creamos el usuario demo
    user = User(
        name="Walter Mancia",
        email=demo_email,
        password_hash=hash_password("demo1234"),
    )
    db.add(user)
    db.flush()  # flush asigna el id sin hacer commit
    print(f"✅ Created demo user: {demo_email} / demo1234")

    # Obtenemos el mapa de categorías por nombre
    categories = db.query(Category).filter(Category.is_default == True).all()
    category_map = {cat.name: cat.id for cat in categories}

    # Creamos las transacciones
    transactions_created = 0
    for t in DEMO_TRANSACTIONS:
        cat_id = category_map.get(t["cat"])
        date = datetime.now(timezone.utc) - timedelta(days=t["days_ago"])

        # Añadimos variación aleatoria pequeña para que los montos
        # no sean todos exactamente iguales — más realista
        amount = Decimal(str(t["amount"])) + Decimal(
            str(random.uniform(-5, 5) if t["type"] == "expense" else 0)
        )
        amount = max(Decimal("1.00"), amount.quantize(Decimal("0.01")))

        transaction = Transaction(
            user_id=user.id,
            category_id=cat_id,
            amount=amount,
            description=t["desc"],
            type=TransactionType(t["type"]),
            date=date,
        )
        db.add(transaction)
        transactions_created += 1

    db.commit()
    print(f"✅ Created {transactions_created} demo transactions.")