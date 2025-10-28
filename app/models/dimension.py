# app/models/dimension.py

"""
Modelos de tabelas dimensionais.

Este módulo define os modelos ORM para entidades de apoio à modelagem
de eventos, como clientes, cidades, buffets, assessorias, insumos,
locais e tipos de evento.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Enum as SQLAlchemyEnum,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class Assessoria(Base):
    """
    Modelo ORM para a tabela 'dim_assessorias'.
    """

    __tablename__ = "dim_assessorias"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    contato = Column(String)
    telefone = Column(String)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="assessorias_criadas")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    eventos = relationship("Evento", back_populates="assessoria")


class Buffet(Base):
    """
    Modelo ORM para a tabela 'dim_buffets'.
    """

    __tablename__ = "dim_buffets"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    contato = Column(String)
    telefone = Column(String)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="buffets_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    eventos = relationship("Evento", back_populates="buffet")


class Cidade(Base):
    """
    Modelo ORM para a tabela 'dim_cidades'.
    """

    __tablename__ = "dim_cidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    estado = Column(String(2), nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="cidades_criadas")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    eventos = relationship("Evento", back_populates="cidade")


class Cliente(Base):
    """
    Modelo ORM para a tabela 'dim_clientes'.
    """

    __tablename__ = "dim_clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    contato_principal = Column(String)
    telefone = Column(String)
    email = Column(String, index=True)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="clientes_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    eventos = relationship("Evento", back_populates="cliente")


class UnidadeMedida(str, enum.Enum):
    """
    Enum para unidades de medida de insumos.
    """

    KG = "KG"
    UNIDADE = "Unidade"
    LITRO = "Litro"


class Insumo(Base):
    """
    Modelo ORM para a tabela 'dim_insumos'.
    """

    __tablename__ = "dim_insumos"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    tipo_insumo = Column(String)
    unidade_medida = Column(SQLAlchemyEnum(UnidadeMedida), nullable=False)
    vlr_referencia = Column(Numeric(10, 2))
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="insumos_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class LocalEvento(Base):
    """
    Modelo ORM para a tabela 'dim_locais_evento'.
    """

    __tablename__ = "dim_locais_evento"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    endereco = Column(String)
    capacidade_maxima = Column(Integer)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="locais_evento_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    eventos = relationship("Evento", back_populates="local_evento")


class TipoEvento(Base):
    """
    Modelo ORM para a tabela 'dim_tipos_evento'.
    """

    __tablename__ = "dim_tipos_evento"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, unique=True, index=True, nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="tipos_evento_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    eventos = relationship("Evento", back_populates="tipo_evento")
