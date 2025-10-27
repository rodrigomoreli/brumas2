# app/schemas/event.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal

# ===================================================================
# SCHEMAS PARA DIMENSÕES RELACIONADAS A EVENTOS
# ===================================================================

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

# ===================================================================
# SCHEMAS PARA FATOS RELACIONADOS A EVENTOS
# ===================================================================

class VendaBase(BaseModel):
    vlr_unitario_por_convidado: Optional[Decimal] = None
    vlr_total_contrato: Decimal
    data_venda: date
    observacoes: Optional[str] = None

class VendaCreate(VendaBase):
    pass

class Venda(VendaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_evento: int
    id_usuario_criador: int

# ===================================================================

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

# ===================================================================
# DESPESA
# ===================================================================

# A classe Base define todos os campos que podem ser enviados pelo usuário
class DespesaBase(BaseModel):
    pass

# A classe de Criação define os campos obrigatórios
class DespesaCreate(DespesaBase):
    id_insumo: int
    quantidade: Decimal
    vlr_unitario_pago: Decimal
    vlr_total_pago: Decimal
    data_despesa: date

# A classe de Atualização herda da Base, mantendo tudo opcional
class DespesaUpdate(DespesaBase):
    pass

# A classe de Resposta representa o objeto completo do banco
class Despesa(DespesaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_evento: int
    id_usuario_criador: int
    id_insumo: Optional[int] = None
    quantidade: Optional[Decimal] = None
    vlr_unitario_pago: Optional[Decimal] = None
    vlr_total_pago: Optional[Decimal] = None
    data_despesa: Optional[date] = None

# ===================================================================


# ===================================================================
# SCHEMAS PARA A TABELA CENTRAL DE EVENTOS
# ===================================================================

class EventoBase(BaseModel):
    id_cliente: int
    id_local_evento: int
    id_tipo_evento: Optional[int] = None
    id_cidade: Optional[int] = None
    id_assessoria: Optional[int] = None
    id_buffet: Optional[int] = None
    data_evento: date
    horas_festa: Optional[Decimal] = None
    qtde_convidados_prevista: Optional[int] = None
    status_evento: Optional[str] = 'Orçamento'

class EventoCreate(EventoBase):
    venda: VendaCreate

class Evento(EventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    venda: Optional[Venda] = None
    degustacoes: list[Degustacao] = []
    despesas: list[Despesa] = []

# ===================================================================
# SCHEMAS PARA O OS CARDS DO FRONT-END
# ===================================================================
class EventoPublic(EventoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_usuario_criador: int
    # Os novos campos que queremos exibir no frontend
    cliente_nome: str
    local_evento_nome: str
    buffet_nome: Optional[str] = None