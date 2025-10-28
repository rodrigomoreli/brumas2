# app/schemas/user.py

"""
Schemas Pydantic para usuários.

Define os modelos de entrada e saída utilizados pela API para operações
relacionadas a usuários, como criação, atualização e leitura.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserProfile


class UserBase(BaseModel):
    """
    Propriedades comuns a todos os schemas de usuário.
    """

    email: EmailStr
    username: str
    nome_completo: Optional[str] = None
    is_active: Optional[bool] = True
    perfil: Optional[UserProfile] = UserProfile.OPERACIONAL


class UserCreate(UserBase):
    """
    Schema para criação de usuário (entrada via API).
    """

    password: str


class UserUpdate(BaseModel):
    """
    Schema para atualização parcial de usuário (entrada via API).
    """

    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    is_active: Optional[bool] = None
    perfil: Optional[UserProfile] = None


class User(UserBase):
    """
    Schema de retorno de usuário (saída da API).
    """

    id: int

    class Config:
        from_attributes = True
