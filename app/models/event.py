# app/models/event.py

from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLAlchemyEnum, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

# Enums para os campos de status
class EventoStatus(str, enum.Enum):
    ORCAMENTO = "Orçamento"
    CONFIRMADO = "Confirmado"
    REALIZADO = "Realizado"
    CANCELADO = "Cancelado"

class DegustacaoStatus(str, enum.Enum):
    AGENDADA = "Agendada"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    data_evento = Column(Date, nullable=False)
    horas_festa = Column(Integer)
    qtde_convidados_prevista = Column(Integer)
    status_evento = Column(SQLAlchemyEnum(EventoStatus), nullable=False, default=EventoStatus.ORCAMENTO)
    
    # Chaves Estrangeiras
    id_cliente = Column(Integer, ForeignKey("dim_clientes.id"), nullable=False)
    id_local_evento = Column(Integer, ForeignKey("dim_locais_evento.id"))
    id_tipo_evento = Column(Integer, ForeignKey("dim_tipos_evento.id"))
    id_cidade = Column(Integer, ForeignKey("dim_cidades.id"))
    id_assessoria = Column(Integer, ForeignKey("dim_assessorias.id"), nullable=True)
    id_buffet = Column(Integer, ForeignKey("dim_buffets.id"), nullable=True)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    vlr_unitario_por_convidado = Column(Numeric(10, 2), nullable=True)
    vlr_total_contrato = Column(Numeric(10, 2), nullable=True)
    data_venda = Column(DateTime, nullable=True)
    observacoes_venda = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    degustacoes = relationship("Degustacao", back_populates="evento", cascade="all, delete-orphan")
    despesas = relationship("Despesa", back_populates="evento", cascade="all, delete-orphan")

class Degustacao(Base):
    __tablename__ = "degustacoes"
    id = Column(Integer, primary_key=True, index=True)
    data_degustacao = Column(Date, nullable=False)
    status = Column(SQLAlchemyEnum(DegustacaoStatus), nullable=False, default=DegustacaoStatus.AGENDADA)
    vlr_degustacao = Column(Numeric(10, 2))
    feedback_cliente = Column(Text)

    # Chaves Estrangeiras
    id_evento = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    evento = relationship("Evento", back_populates="degustacoes")

class Despesa(Base):
    __tablename__ = "despesas"
    id = Column(Integer, primary_key=True, index=True)
    quantidade = Column(Numeric(10, 2), nullable=False)
    vlr_unitario_pago = Column(Numeric(10, 2), nullable=False)
    vlr_total_pago = Column(Numeric(10, 2), nullable=False)
    data_despesa = Column(Date, nullable=False)

    # Chaves Estrangeiras
    id_evento = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    id_insumo = Column(Integer, ForeignKey("dim_insumos.id"), nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    evento = relationship("Evento", back_populates="despesas")
