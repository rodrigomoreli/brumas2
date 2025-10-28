# app/db/base.py

"""
Classe base para os modelos ORM.

Este módulo define a classe Base usada como superclasse para todos os
modelos SQLAlchemy da aplicação. Ela serve como ponto comum para o
mapeamento objeto-relacional.
"""

from sqlalchemy.ext.declarative import declarative_base

# Classe base para os modelos ORM
Base = declarative_base()
