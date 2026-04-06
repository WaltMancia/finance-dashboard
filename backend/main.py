from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.interfaces.routes import (
    auth_router, category_router,
    transaction_router, csv_router, analytics_router,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# En producción solo permitimos el dominio de Vercel
# En desarrollo permitimos localhost
allowed_origins = [settings.frontend_url]
if settings.debug:
    allowed_origins.extend([
        "http://localhost:5173",
        "http://localhost:3000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(category_router.router, prefix="/api/v1")
app.include_router(transaction_router.router, prefix="/api/v1")
app.include_router(csv_router.router, prefix="/api/v1")
app.include_router(analytics_router.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }