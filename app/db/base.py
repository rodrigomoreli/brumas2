# app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

# Cria a classe Base que será usada por todos os modelos do SQLAlchemy.
# Nossos modelos (User, Evento, Cliente, etc.) herdarão desta classe.
Base = declarative_base()
