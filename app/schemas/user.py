# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserProfile

# Propriedades compartilhadas por todos os schemas de usuário
class UserBase(BaseModel):
    email: EmailStr
    username: str
    nome_completo: Optional[str] = None
    is_active: Optional[bool] = True
    perfil: Optional[UserProfile] = UserProfile.OPERACIONAL

# Schema para a criação de um usuário (recebido pela API)
# Herda de UserBase e adiciona o campo de senha
class UserCreate(UserBase):
    password: str

# Schema para a atualização de um usuário (recebido pela API)
# Todos os campos são opcionais
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    is_active: Optional[bool] = None
    perfil: Optional[UserProfile] = None

# Schema para a resposta da API (enviado pela API)
# Não inclui o campo 'hashed_password' por segurança
class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Permite que o Pydantic leia dados de objetos SQLAlchemy
