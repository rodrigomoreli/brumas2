# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Union, Optional
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # --- Configurações da API ---
    PROJECT_NAME: str = "Brumas API"
    API_V1_STR: str = "/api/v1"

    # --- Configurações de Segurança (JWT) ---
    # Esta chave secreta é usada para assinar os tokens JWT.
    # É CRUCIAL que seja um valor longo, aleatório e mantido em segredo.
    SECRET_KEY: Optional[str] = None
    # O algoritmo usado para a assinatura do token.
    ALGORITHM: str = "HS256"
    # Tempo de vida do token de acesso em minutos.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 dias

    # --- Configurações do Banco de Dados ---
    DATABASE_URL: Optional[str] = None

    # --- Configurações de CORS (Cross-Origin Resource Sharing) ---
    # Lista de origens que têm permissão para acessar a API.
    # Essencial para conectar um frontend no futuro.
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        # O Pydantic tentará ler as variáveis de um arquivo .env
        case_sensitive = True
        env_file = ".env"

# Cria uma instância única das configurações que será importada pelo resto da aplicação
settings = Settings()

# Verificação em tempo de execução para garantir que valores críticos foram fornecidos
if not settings.SECRET_KEY or not settings.DATABASE_URL:
    raise RuntimeError(
        "Missing required configuration: SECRET_KEY and DATABASE_URL must be set "
        "as environment variables or provided in the .env file."
    )
