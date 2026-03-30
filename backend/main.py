from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.interfaces.routes import auth_router, category_router, transaction_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    # Swagger disponible en /docs
    # ReDoc disponible en /redoc
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefijo global /api/v1 para todas las rutas
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(category_router.router, prefix="/api/v1")
app.include_router(transaction_router.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }