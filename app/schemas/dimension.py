# COMO CRIAR, ATUALIZAR E RETORNAR OBJETOS DE DIMENSÃO

from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal
import enum
from pydantic import EmailStr

# ===================================================================
# --- Assessoria ---
# ===================================================================

class AssessoriaBase(BaseModel):
    descricao: Optional[str] = None
    contato: Optional[str] = None
    telefone: Optional[str] = None

class AssessoriaCreate(AssessoriaBase):
    descricao: Optional[str] = None

class AssessoriaUpdate(AssessoriaBase): 
    pass

class Assessoria(AssessoriaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime

# ===================================================================
# --- Buffet ---
# ===================================================================

class BuffetBase(BaseModel):
    descricao: Optional[str] = None
    contato: Optional[str] = None
    telefone: Optional[str] = None

class BuffetCreate(BuffetBase):
    descricao: Optional[str] = None

class BuffetUpdate(BuffetBase):
    pass

class Buffet(BuffetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime

# ===================================================================
# --- Cidade ---
# ===================================================================

class CidadeBase(BaseModel):
    nome: Optional[str] = None
    estado: Optional[str] = None

class CidadeCreate(CidadeBase):
    nome: Optional[str] = None
    estado: Optional[str] = None

class CidadeUpdate(CidadeBase):
    pass

class Cidade(CidadeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime

# ===================================================================
# --- Cliente ---
# ===================================================================

# A classe Base reflete os campos que podem ser enviados pelo usuário
# Todos são opcionais para máxima flexibilidade
class ClienteBase(BaseModel):
    nome: Optional[str] = None
    contato_principal: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None

# A classe de Criação herda da Base e define quais campos são
# obrigatórios ao criar um novo cliente.
class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr

# A classe de Atualização herda da Base, mantendo todos os campos
# opcionais para permitir atualizações parciais (PATCH).
class ClienteUpdate(ClienteBase):
    pass

# A classe principal (de resposta) representa o objeto completo
# como ele existe no banco de dados, incluindo campos automáticos.
class Cliente(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime

# ===================================================================
# --- Insumo ---
# ===================================================================

class UnidadeMedida(str, enum.Enum):
    KG = "KG"
    UNIDADE = "Unidade"
    LITRO = "Litro"

class InsumoBase(BaseModel):
    descricao: Optional[str] = None
    unidade_medida: Optional[UnidadeMedida] = None

class InsumoCreate(InsumoBase):
    descricao: Optional[str] = None
    unidade_medida: Optional[UnidadeMedida] = None

class InsumoUpdate(InsumoBase):
    pass

class Insumo(InsumoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime

# ===================================================================
# --- LocalEvento ---
# ===================================================================

class LocalEventoBase(BaseModel):
    descricao: Optional[str] = None
    contato: Optional[str] = None
    telefone: Optional[str] = None

class LocalEventoCreate(LocalEventoBase):
    descricao: Optional[str] = None

class LocalEventoUpdate(LocalEventoBase):
    pass

class LocalEvento(LocalEventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime


# ===================================================================
# --- TipoEvento ---
# ===================================================================

class TipoEventoBase(BaseModel):
    descricao: Optional[str] = None

class TipoEventoCreate(TipoEventoBase):
    descricao: Optional[str] = None

class TipoEventoUpdate(TipoEventoBase):
    pass

class TipoEvento(TipoEventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime
