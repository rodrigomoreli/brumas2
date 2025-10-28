# app/models/dimension.py
# OS MODELOS DE DIMENSÃO. É PARA O SQLALCHEMY SAIBA COMO CRIAR AS TABELAS NO BANCO DE DADOS.
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
import enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
# Removido 'from .user import User' para evitar importação circular, o SQLAlchemy resolve por string.
from app.db.base import Base

# Modelo de Dimensão para Assessorias
class Assessoria(Base):
    __tablename__ = "dim_assessorias"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    contato = Column(String)
    telefone = Column(String)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="assessorias_criadas")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # <<< ADICIONADO: Relação de volta para a tabela de eventos
    eventos = relationship("Evento", back_populates="assessoria")

# Modelo de Dimensão para Buffets
class Buffet(Base):
    __tablename__ = "dim_buffets"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    contato = Column(String)
    telefone = Column(String)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="buffets_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # <<< ADICIONADO: Relação de volta para a tabela de eventos
    eventos = relationship("Evento", back_populates="buffet")

# Modelo de Dimensão para Cidades
class Cidade(Base):
    __tablename__ = "dim_cidades"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    estado = Column(String(2), nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="cidades_criadas") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # <<< ADICIONADO: Relação de volta para a tabela de eventos
    eventos = relationship("Evento", back_populates="cidade")

# Modelo de Dimensão para Clientes
class Cliente(Base):
    __tablename__ = "dim_clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    contato_principal = Column(String)
    telefone = Column(String)
    email = Column(String, index=True)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="clientes_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # <<< ADICIONADO: Relação de volta para a tabela de eventos
    eventos = relationship("Evento", back_populates="cliente")

# Modelo de Dimensão para Unidades de Medida de Insumos
class UnidadeMedida(str, enum.Enum):
    KG = "KG"
    UNIDADE = "Unidade"
    LITRO = "Litro"

# Modelo de Dimensão para Insumos
class Insumo(Base):
    __tablename__ = "dim_insumos"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    tipo_insumo = Column(String)
    unidade_medida = Column(SQLAlchemyEnum(UnidadeMedida), nullable=False)
    vlr_referencia = Column(Numeric(10, 2))
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="insumos_criados")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Modelo de Dimensão para Locais de Evento
class LocalEvento(Base):
    __tablename__ = "dim_locais_evento"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True, nullable=False)
    endereco = Column(String)
    capacidade_maxima = Column(Integer)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="locais_evento_criados") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # <<< ADICIONADO: Relação de volta para a tabela de eventos
    eventos = relationship("Evento", back_populates="local_evento")

# Modelo de Dimensão para Tipos de Evento
class TipoEvento(Base):
    __tablename__ = "dim_tipos_evento"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, unique=True, index=True, nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_criador = relationship("User", back_populates="tipos_evento_criados") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # <<< ADICIONADO: Relação de volta para a tabela de eventos
    eventos = relationship("Evento", back_populates="tipo_evento")
