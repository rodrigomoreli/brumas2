# app/schemas/token.py

"""
Schemas Pydantic para autenticação.

Define os modelos utilizados para representar tokens JWT e seus dados
decodificados, usados nos processos de login e autorização.
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """
    Representa o token JWT retornado após autenticação.
    """

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Representa os dados decodificados de um token JWT.
    """

    sub: Optional[int] = None
