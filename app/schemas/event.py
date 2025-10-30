# app/schemas/event.py

"""
Schemas Pydantic para eventos, despesas e degustações.
Define os modelos utilizados pela API para entrada, saída e exibição
de dados relacionados à gestão de eventos.
"""

from pydantic import BaseModel, ConfigDict, Field
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


class EventoStats(BaseModel):
    """Estatísticas gerais de eventos."""

    total_eventos: int = Field(description="Total de eventos no período")
    eventos_orcamento: int = Field(description="Eventos com status Orçamento")
    eventos_confirmados: int = Field(description="Eventos com status Confirmado")
    eventos_realizados: int = Field(description="Eventos com status Realizado")
    eventos_cancelados: int = Field(description="Eventos com status Cancelado")

    valor_total_contratos: Decimal = Field(description="Soma de todos os contratos")
    valor_medio_contrato: Decimal = Field(description="Valor médio por contrato")
    valor_total_orcamentos: Decimal = Field(description="Valor total dos orçamentos")
    valor_total_confirmados: Decimal = Field(
        description="Valor total dos eventos confirmados"
    )

    total_convidados_previsto: int = Field(description="Total de convidados previstos")
    media_convidados_por_evento: float = Field(
        description="Média de convidados por evento"
    )

    total_despesas: Decimal = Field(description="Total gasto em despesas")
    total_degustacoes: int = Field(description="Total de degustações realizadas")
    valor_total_degustacoes: Decimal = Field(
        description="Valor total gasto em degustações"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_eventos": 45,
                "eventos_orcamento": 12,
                "eventos_confirmados": 20,
                "eventos_realizados": 10,
                "eventos_cancelados": 3,
                "valor_total_contratos": "850000.00",
                "valor_medio_contrato": "18888.89",
                "valor_total_orcamentos": "240000.00",
                "valor_total_confirmados": "520000.00",
                "total_convidados_previsto": 6750,
                "media_convidados_por_evento": 150.0,
                "total_despesas": "125000.00",
                "total_degustacoes": 35,
                "valor_total_degustacoes": "17500.00",
            }
        }


class EventosPorMes(BaseModel):
    """Eventos agrupados por mês."""

    mes: str = Field(description="Mês no formato YYYY-MM")
    total_eventos: int = Field(description="Total de eventos no mês")
    valor_total: Decimal = Field(description="Valor total dos contratos no mês")

    class Config:
        json_schema_extra = {
            "example": {
                "mes": "2025-12",
                "total_eventos": 8,
                "valor_total": "144000.00",
            }
        }


class EventosPorStatus(BaseModel):
    """Eventos agrupados por status."""

    status: str = Field(description="Status do evento")
    total: int = Field(description="Quantidade de eventos com este status")
    percentual: float = Field(description="Percentual do total")
    valor_total: Decimal = Field(description="Valor total dos contratos neste status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "Confirmado",
                "total": 20,
                "percentual": 44.4,
                "valor_total": "520000.00",
            }
        }


class TopClientes(BaseModel):
    """Top clientes por valor de contratos."""

    id_cliente: int
    cliente_nome: str
    total_eventos: int = Field(description="Total de eventos do cliente")
    valor_total: Decimal = Field(description="Valor total dos contratos")

    class Config:
        json_schema_extra = {
            "example": {
                "id_cliente": 5,
                "cliente_nome": "Maria Silva",
                "total_eventos": 3,
                "valor_total": "54000.00",
            }
        }


class DespesasPorInsumo(BaseModel):
    """Despesas agrupadas por insumo."""

    id_insumo: int
    insumo_descricao: str
    quantidade_total: Decimal = Field(description="Quantidade total consumida")
    valor_total: Decimal = Field(description="Valor total gasto")
    numero_eventos: int = Field(description="Número de eventos que usaram este insumo")

    class Config:
        json_schema_extra = {
            "example": {
                "id_insumo": 12,
                "insumo_descricao": "Carne Bovina",
                "quantidade_total": "450.50",
                "valor_total": "22525.00",
                "numero_eventos": 15,
            }
        }


class DashboardData(BaseModel):
    """Dados completos para dashboard."""

    estatisticas_gerais: EventoStats
    eventos_por_mes: list[EventosPorMes]
    eventos_por_status: list[EventosPorStatus]
    top_clientes: list[TopClientes]
    despesas_por_insumo: list[DespesasPorInsumo]

    class Config:
        json_schema_extra = {
            "example": {
                "estatisticas_gerais": {"total_eventos": 45},
                "eventos_por_mes": [{"mes": "2025-12", "total_eventos": 8}],
                "eventos_por_status": [{"status": "Confirmado", "total": 20}],
                "top_clientes": [{"id_cliente": 5, "cliente_nome": "Maria Silva"}],
                "despesas_por_insumo": [
                    {"id_insumo": 12, "insumo_descricao": "Carne Bovina"}
                ],
            }
        }
