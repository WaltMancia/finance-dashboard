# ── ETAPA 1: Dependencias ──────────────────────────────────
FROM python:3.11-slim AS dependencies

WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg2
# --no-install-recommends reduce el tamaño de la imagen
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiamos SOLO requirements.txt primero
# Si el código cambia pero requirements no → Docker usa caché de esta capa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ── ETAPA 2: Producción ────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Copiamos solo lo necesario de la etapa anterior
# La imagen final NO incluye gcc ni otras herramientas de build
COPY --from=dependencies /usr/local/lib/python3.11/site-packages \
    /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Instalamos libpq en producción (runtime de PostgreSQL)
RUN apt-get update && apt-get install -y \
    libpq5 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el código
COPY . .

# Usuario no-root por seguridad
# Nunca corras aplicaciones en producción como root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

# Comando de producción:
# --workers 2 → dos procesos para manejar más peticiones en paralelo
# --host 0.0.0.0 → acepta conexiones de cualquier IP
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]