from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers import users, login, dimensions, eventos

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuração do CORS (Cross-Origin Resource Sharing)
# Isso é essencial para permitir que um frontend web (rodando em outro domínio) possa fazer requisições para esta API.
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclui os routers na aplicação principal, definindo seus prefixos
app.include_router(login.router, tags=["Login"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(dimensions.router, prefix=f"{settings.API_V1_STR}/dimensions", tags=["Dimensions"])
app.include_router(eventos.router, prefix=f"{settings.API_V1_STR}/eventos", tags=["Eventos"])

@app.get("/")
def read_root():
    return {"message": f"Bem-vindo à API do {settings.PROJECT_NAME}"}
