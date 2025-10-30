# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.middleware.logging import LoggingMiddleware
from app.api.routers import users, login, dimensions, eventos

# Instância principal da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Middleware de logging
app.add_middleware(LoggingMiddleware)

# Configuração do CORS para permitir acesso de frontends externos
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Registro dos routers da aplicação
app.include_router(login.router, tags=["Login"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(
    dimensions.router, prefix=f"{settings.API_V1_STR}/dimensions", tags=["Dimensions"]
)
app.include_router(
    eventos.router, prefix=f"{settings.API_V1_STR}/eventos", tags=["Eventos"]
)


@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar a aplicação."""
    logger.info(
        f"🚀 Aplicação iniciada: {settings.PROJECT_NAME}",
        extra={
            "environment": settings.ENVIRONMENT,
            "api_version": settings.API_V1_STR,
        },
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado ao encerrar a aplicação."""
    logger.info(
        f"🛑 Aplicação encerrada: {settings.PROJECT_NAME}",
        extra={
            "environment": settings.ENVIRONMENT,
        },
    )


@app.get("/")
def read_root():
    """Endpoint raiz da API."""
    logger.info("Root endpoint accessed")
    return {"message": f"Bem-vindo à API do {settings.PROJECT_NAME}"}


@app.get("/health")
def health_check():
    """Endpoint de health check para monitoramento."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
