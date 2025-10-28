# app/core/config.py

"""
Configurações globais da aplicação.

Este módulo define a classe Settings, responsável por carregar e validar
variáveis de ambiente usando Pydantic. As configurações incluem dados da API,
segurança, banco de dados e CORS.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Configurações da API
    PROJECT_NAME: str = "Brumas API"
    API_V1_STR: str = "/api/v1"

    # Configurações de segurança (JWT)
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Configuração do banco de dados
    DATABASE_URL: Optional[str] = None

    # Configurações de CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

if not settings.SECRET_KEY or not settings.DATABASE_URL:
    raise RuntimeError(
        "SECRET_KEY e DATABASE_URL devem estar definidos nas variáveis "
        "de ambiente ou no arquivo .env."
    )
