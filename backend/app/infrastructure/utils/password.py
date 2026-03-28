from passlib.context import CryptContext

# CryptContext gestiona el hashing de contraseñas
# bcrypt es el algoritmo recomendado — lento por diseño para dificultar ataques
# deprecated="auto" → migra automáticamente a algoritmos más nuevos si es necesario
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a un hash seguro."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)