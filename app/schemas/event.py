# app/schemas/event.py

"""
Schemas Pydantic para eventos, insumos, despesas e degustações.

Define os modelos utilizados pela API para entrada, saída e exibição
de dados relacionados à gestão de eventos.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


# Schemas de Insumo


class InsumoBase(BaseModel):
    descricao: str
    tipo_insumo: Optional[str] = None
    unidade_medida: Optional[str] = None
    vlr_referencia: Optional[Decimal] = None


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(InsumoBase):
    pass


class Insumo(InsumoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Schemas de Degustação


class DegustacaoBase(BaseModel):
    vlr_degustacao: Optional[Decimal] = None
    feedback_cliente: Optional[str] = None


class DegustacaoCreate(DegustacaoBase):
    data_degustacao: date
    status: str = "Agendada"


class DegustacaoUpdate(DegustacaoBase):
    pass


class Degustacao(DegustacaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_evento: int
    id_usuario_criador: int


# Schemas de Despesa


class DespesaBase(BaseModel):
    """Campos opcionais para criação ou atualização de despesas."""

    pass


class DespesaCreate(DespesaBase):
    """Campos obrigatórios para criação de uma despesa."""

    id_insumo: int
    quantidade: Decimal
    vlr_unitario_pago: Decimal
    vlr_total_pago: Decimal
    data_despesa: date


class DespesaUpdate(DespesaBase):
    """Atualização parcial de uma despesa."""

    pass


class Despesa(DespesaBase):
    """Representação completa de uma despesa."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    id_evento: int
    id_usuario_criador: int
    id_insumo: Optional[int] = None
    quantidade: Optional[Decimal] = None
    vlr_unitario_pago: Optional[Decimal] = None
    vlr_total_pago: Optional[Decimal] = None
    data_despesa: Optional[date] = None


# Schemas de Evento


class EventoBase(BaseModel):
    id_cliente: int
    id_local_evento: int
    id_tipo_evento: Optional[int] = None
    id_cidade: Optional[int] = None
    id_assessoria: Optional[int] = None
    id_buffet: Optional[int] = None
    data_evento: Optional[date] = None
    horas_festa: Optional[Decimal] = None
    qtde_convidados_prevista: Optional[int] = None
    status_evento: Optional[str] = "Orçamento"
    vlr_unitario_por_convidado: Optional[Decimal] = None
    vlr_total_contrato: Optional[Decimal] = None
    data_venda: Optional[datetime] = None
    observacoes_venda: Optional[str] = None


class EventoCreate(EventoBase):
    pass


class EventoUpdate(EventoBase):
    id_cliente: Optional[int] = None
    id_local_evento: Optional[int] = None
    id_tipo_evento: Optional[int] = None
    id_cidade: Optional[int] = None
    id_assessoria: Optional[int] = None
    id_buffet: Optional[int] = None
    data_evento: Optional[date] = None
    horas_festa: Optional[Decimal] = None
    qtde_convidados_prevista: Optional[int] = None
    status_evento: Optional[str] = None
    vlr_unitario_por_convidado: Optional[Decimal] = None
    vlr_total_contrato: Optional[Decimal] = None
    data_venda: Optional[datetime] = None
    observacoes_venda: Optional[str] = None


class Evento(EventoBase):
    """Representação completa de um evento."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    degustacoes: list[Degustacao] = []
    despesas: list[Despesa] = []
    created_at: datetime
    updated_at: datetime


class EventoPublic(EventoBase):
    """Modelo simplificado para exibição em cards no frontend."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    cliente_nome: str
    local_evento_nome: str
    buffet_nome: Optional[str] = None


class EventoDetail(Evento):
    """Modelo detalhado para exibição na tela de detalhes."""

    model_config = ConfigDict(from_attributes=True)
    cliente_nome: Optional[str] = None
    local_evento_nome: Optional[str] = None
    tipo_evento_nome: Optional[str] = None
    cidade_nome: Optional[str] = None
    assessoria_nome: Optional[str] = None
    buffet_nome: Optional[str] = None
    id_usuario_criador_nome: Optional[str] = None
