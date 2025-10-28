# app/db/session.py

"""
Configuração da sessão de banco de dados.

Este módulo define o motor de conexão e a fábrica de sessões do SQLAlchemy,
utilizando as configurações definidas no módulo de configuração da aplicação.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Cria o motor de conexão com base na URL definida nas configurações
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica a conexão antes de reutilizá-la
)

# Fábrica de sessões para interação com o banco de dados
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
