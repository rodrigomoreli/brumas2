# app/schemas/dimension.py

"""
Schemas Pydantic para entidades dimensionais.

Define os modelos utilizados pela API para criação, atualização e
retorno de dados relacionados a assessorias, buffets, cidades,
clientes, insumos, locais e tipos de evento.
"""

from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional
import enum


# Assessoria


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


# Buffet


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


# Cidade


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


# Cliente


class ClienteBase(BaseModel):
    nome: Optional[str] = None
    contato_principal: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr


class ClienteUpdate(ClienteBase):
    nome: Optional[str] = None
    contato_principal: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class Cliente(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime


# Insumo


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


# LocalEvento


class LocalEventoBase(BaseModel):
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    capacidade_maxima: Optional[int] = None


class LocalEventoCreate(LocalEventoBase):
    descricao: Optional[str] = None
    updated_at: Optional[datetime] = None


class LocalEventoUpdate(LocalEventoBase):
    pass


class LocalEvento(LocalEventoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_usuario_criador: int
    created_at: datetime
    updated_at: datetime


# TipoEvento


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
