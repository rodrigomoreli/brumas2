"""
Schemas Pydantic para eventos, despesas e degustações.
Define os modelos utilizados pela API para entrada, saída e exibição
de dados relacionados à gestão de eventos.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


# Schemas de Degustação
class DegustacaoBase(BaseModel):
    data_degustacao: Optional[date] = None
    vlr_degustacao: Optional[Decimal] = None
    feedback_cliente: Optional[str] = None
    status: Optional[str] = None


class DegustacaoCreate(BaseModel):
    data_degustacao: date  # Obrigatório
    status: str = "Agendada"
    vlr_degustacao: Optional[Decimal] = None
    feedback_cliente: Optional[str] = None


class DegustacaoUpdate(DegustacaoBase):
    """Atualização parcial de uma degustação."""

    pass


class Degustacao(DegustacaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_evento: int
    id_usuario_criador: int
    data_degustacao: date
    status: str
    created_at: datetime
    updated_at: datetime


# Schemas de Despesa
class DespesaBase(BaseModel):
    """Campos opcionais para criação ou atualização de despesas."""

    id_insumo: Optional[int] = None
    quantidade: Optional[Decimal] = None
    vlr_unitario_pago: Optional[Decimal] = None
    vlr_total_pago: Optional[Decimal] = None
    data_despesa: Optional[date] = None


class DespesaCreate(BaseModel):
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
    id_insumo: int
    quantidade: Decimal
    vlr_unitario_pago: Decimal
    vlr_total_pago: Decimal
    data_despesa: date
    created_at: datetime
    updated_at: datetime


# Schemas de Evento
class EventoBase(BaseModel):
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


class EventoCreate(BaseModel):
    # Campos obrigatórios
    id_cliente: int
    id_local_evento: int
    data_evento: date

    # Campos opcionais
    id_tipo_evento: Optional[int] = None
    id_cidade: Optional[int] = None
    id_assessoria: Optional[int] = None
    id_buffet: Optional[int] = None
    horas_festa: Optional[Decimal] = None
    qtde_convidados_prevista: Optional[int] = None
    status_evento: Optional[str] = "Orçamento"
    vlr_unitario_por_convidado: Optional[Decimal] = None
    vlr_total_contrato: Optional[Decimal] = None
    data_venda: Optional[datetime] = None
    observacoes_venda: Optional[str] = None


class EventoUpdate(EventoBase):
    """Todos os campos opcionais para atualização parcial."""

    pass


class Evento(EventoBase):
    """Representação completa de um evento."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    id_cliente: int
    id_local_evento: int
    data_evento: date
    status_evento: str
    degustacoes: list[Degustacao] = []
    despesas: list[Despesa] = []
    created_at: datetime
    updated_at: datetime


class EventoPublic(BaseModel):
    """Modelo simplificado para exibição em cards no frontend."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    id_cliente: int
    id_local_evento: int
    data_evento: date
    status_evento: str
    cliente_nome: Optional[str] = None
    local_evento_nome: Optional[str] = None
    buffet_nome: Optional[str] = None
    qtde_convidados_prevista: Optional[int] = None
    vlr_total_contrato: Optional[Decimal] = None


class EventoDetail(Evento):
    """Modelo detalhado para exibição na tela de detalhes."""

    model_config = ConfigDict(from_attributes=True)
    cliente_nome: Optional[str] = None
    local_evento_nome: Optional[str] = None
    tipo_evento_nome: Optional[str] = None
    cidade_nome: Optional[str] = None
    assessoria_nome: Optional[str] = None
    buffet_nome: Optional[str] = None
    usuario_criador_nome: Optional[str] = None
