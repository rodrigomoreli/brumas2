"""
Modelos relacionados a eventos.
Este módulo define os modelos ORM para eventos, despesas e degustações.
Inclui enums de status, relacionamentos entre entidades e propriedades
híbridas para facilitar a leitura por Pydantic.
"""

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Date,
    Enum as SQLAlchemyEnum,
    Numeric,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class EventoStatus(str, enum.Enum):
    """
    Enum para status de um evento.
    """

    ORCAMENTO = "Orçamento"
    CONFIRMADO = "Confirmado"
    REALIZADO = "Realizado"
    CANCELADO = "Cancelado"


class DegustacaoStatus(str, enum.Enum):
    """
    Enum para status de uma degustação.
    """

    AGENDADA = "Agendada"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"


class Evento(Base):
    """
    Modelo ORM para a tabela 'eventos'.
    """

    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    data_evento = Column(Date, nullable=False)
    horas_festa = Column(Numeric(10, 2))
    qtde_convidados_prevista = Column(Integer)
    status_evento = Column(
        SQLAlchemyEnum(EventoStatus),
        nullable=False,
        default=EventoStatus.ORCAMENTO,
    )

    id_cliente = Column(Integer, ForeignKey("dim_clientes.id"), nullable=False)
    id_local_evento = Column(
        Integer, ForeignKey("dim_locais_evento.id"), nullable=False
    )
    id_tipo_evento = Column(Integer, ForeignKey("dim_tipos_evento.id"))
    id_cidade = Column(Integer, ForeignKey("dim_cidades.id"))
    id_assessoria = Column(Integer, ForeignKey("dim_assessorias.id"))
    id_buffet = Column(Integer, ForeignKey("dim_buffets.id"))
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    vlr_unitario_por_convidado = Column(Numeric(10, 2))
    vlr_total_contrato = Column(Numeric(10, 2))
    data_venda = Column(DateTime)
    observacoes_venda = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,  # ✅ Não pode ser NULL
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,  # ✅ Não pode ser NULL
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="eventos")
    local_evento = relationship("LocalEvento", back_populates="eventos")
    tipo_evento = relationship("TipoEvento", back_populates="eventos")
    cidade = relationship("Cidade", back_populates="eventos")
    assessoria = relationship("Assessoria", back_populates="eventos")
    buffet = relationship("Buffet", back_populates="eventos")
    usuario_criador = relationship("User")

    degustacoes = relationship(
        "Degustacao",
        back_populates="evento",
        cascade="all, delete-orphan",
    )
    despesas = relationship(
        "Despesa",
        back_populates="evento",
        cascade="all, delete-orphan",
    )

    # Propriedades híbridas para leitura por Pydantic
    @hybrid_property
    def cliente_nome(self):
        return self.cliente.nome if self.cliente else None

    @hybrid_property
    def local_evento_nome(self):
        return self.local_evento.descricao if self.local_evento else None

    @hybrid_property
    def buffet_nome(self):
        return self.buffet.descricao if self.buffet else None

    @hybrid_property
    def tipo_evento_nome(self):
        return self.tipo_evento.descricao if self.tipo_evento else None

    @hybrid_property
    def cidade_nome(self):
        return self.cidade.nome if self.cidade else None

    @hybrid_property
    def assessoria_nome(self):
        return self.assessoria.descricao if self.assessoria else None

    @hybrid_property
    def usuario_criador_nome(self):
        return self.usuario_criador.nome_completo if self.usuario_criador else None


class Despesa(Base):
    """
    Modelo ORM para a tabela 'despesas'.
    """

    __tablename__ = "despesas"

    id = Column(Integer, primary_key=True, index=True)
    quantidade = Column(Numeric(10, 2), nullable=False)
    vlr_unitario_pago = Column(Numeric(10, 2), nullable=False)
    vlr_total_pago = Column(Numeric(10, 2), nullable=False)
    data_despesa = Column(Date, nullable=False)

    id_evento = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    id_insumo = Column(Integer, ForeignKey("dim_insumos.id"), nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    evento = relationship("Evento", back_populates="despesas")
    insumo = relationship("Insumo")
    usuario_criador = relationship("User")


class Degustacao(Base):
    """
    Modelo ORM para a tabela 'degustacoes'.
    """

    __tablename__ = "degustacoes"

    id = Column(Integer, primary_key=True, index=True)
    data_degustacao = Column(Date, nullable=False)
    status = Column(
        SQLAlchemyEnum(DegustacaoStatus),
        nullable=False,
        default=DegustacaoStatus.AGENDADA,
    )
    vlr_degustacao = Column(Numeric(10, 2))
    feedback_cliente = Column(Text)

    id_evento = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    id_usuario_criador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    evento = relationship("Evento", back_populates="degustacoes")
    usuario_criador = relationship("User")
