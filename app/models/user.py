# app/models/user.py

"""
Modelo de dados do usuário.
Define a estrutura da tabela de usuários, incluindo atributos, tipos,
restrições e relacionamentos com outras entidades da aplicação.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class UserProfile(str, enum.Enum):
    """
    Enum para perfis de acesso do usuário.
    """

    ADMINISTRATIVO = "administrativo"
    OPERACIONAL = "operacional"


class User(Base):
    """
    Modelo ORM para a tabela 'usuarios'.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nome_completo = Column(String, index=True)
    perfil = Column(
        SQLAlchemyEnum(UserProfile),
        nullable=False,
        default=UserProfile.OPERACIONAL,
    )
    is_active = Column(Boolean(), default=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relacionamentos com outras entidades
    assessorias_criadas = relationship(
        "Assessoria",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Assessoria.id_usuario_criador]",
    )
    buffets_criados = relationship(
        "Buffet",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Buffet.id_usuario_criador]",
    )
    cidades_criadas = relationship(
        "Cidade",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Cidade.id_usuario_criador]",
    )
    clientes_criados = relationship(
        "Cliente",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Cliente.id_usuario_criador]",
    )
    insumos_criados = relationship(
        "Insumo",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Insumo.id_usuario_criador]",
    )
    locais_evento_criados = relationship(
        "LocalEvento",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[LocalEvento.id_usuario_criador]",
    )
    tipos_evento_criados = relationship(
        "TipoEvento",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[TipoEvento.id_usuario_criador]",
    )

    # RELACIONAMENTOS: Eventos, Despesas e Degustações
    eventos_criados = relationship(
        "Evento",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Evento.id_usuario_criador]",
    )
    despesas_criadas = relationship(
        "Despesa",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Despesa.id_usuario_criador]",
    )
    degustacoes_criadas = relationship(
        "Degustacao",
        back_populates="usuario_criador",
        cascade="all, delete-orphan",
        foreign_keys="[Degustacao.id_usuario_criador]",
    )
