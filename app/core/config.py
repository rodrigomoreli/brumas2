# app/core/config.py
"""
Configurações globais da aplicação.
Este módulo define a classe Settings, responsável por carregar e validar
variáveis de ambiente usando Pydantic. As configurações incluem dados da API,
segurança, banco de dados e CORS.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import json


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

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Converte string JSON do .env em lista Python.
        Aceita formatos:
        - String JSON: '["http://localhost:5173"]'
        - String separada por vírgula: "http://localhost:5173,http://localhost:3000"
        - Lista Python: ["http://localhost:5173"]
        """
        if isinstance(v, str) and not v.startswith("["):
            # Formato: "url1,url2,url3"
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            # Formato: '["url1", "url2"]'
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        elif isinstance(v, list):
            # Já é uma lista
            return v
        return []

    # Configurações de Log
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    ENVIRONMENT: str = "development"  # development, staging, production

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

if not settings.SECRET_KEY or not settings.DATABASE_URL:
    raise RuntimeError(
        "SECRET_KEY e DATABASE_URL devem estar definidos nas variáveis "
        "de ambiente ou no arquivo .env."
    )
