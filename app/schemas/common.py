# app/schemas/common.py

"""
Schemas comuns utilizados em toda a aplicação.
Define modelos genéricos reutilizáveis como paginação e respostas padrão.
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Schema genérico para respostas paginadas.

    Attributes:
        items: Lista de itens da página atual
        total: Total de itens no banco (considerando filtros)
        page: Número da página atual (começa em 1)
        page_size: Quantidade de itens por página
        total_pages: Total de páginas disponíveis
        has_next: Se existe próxima página
        has_previous: Se existe página anterior
    """

    items: List[T] = Field(description="Lista de itens da página atual")
    total: int = Field(description="Total de itens (considerando filtros)")
    page: int = Field(description="Número da página atual", ge=1)
    page_size: int = Field(description="Quantidade de itens por página", ge=1)
    total_pages: int = Field(description="Total de páginas disponíveis", ge=0)
    has_next: bool = Field(description="Indica se existe próxima página")
    has_previous: bool = Field(description="Indica se existe página anterior")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "data_evento": "2025-12-15",
                        "status_evento": "Confirmado",
                    }
                ],
                "total": 150,
                "page": 1,
                "page_size": 20,
                "total_pages": 8,
                "has_next": True,
                "has_previous": False,
            }
        }


class MessageResponse(BaseModel):
    """
    Schema para respostas simples com mensagem.
    Útil para confirmações de operações.
    """

    message: str = Field(description="Mensagem de resposta")
    detail: Optional[str] = Field(None, description="Detalhes adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operação realizada com sucesso",
                "detail": "O evento foi criado e notificações foram enviadas",
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema para respostas de erro padronizadas.
    """

    error: str = Field(description="Tipo do erro")
    message: str = Field(description="Mensagem descritiva do erro")
    detail: Optional[str] = Field(None, description="Detalhes técnicos do erro")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Dados inválidos fornecidos",
                "detail": "O campo 'data_evento' deve estar no formato YYYY-MM-DD",
            }
        }
