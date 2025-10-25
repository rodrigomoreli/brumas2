from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from passlib.context import CryptContext # O import continua o mesmo
from jose import jwt

from app.core.config import settings

# Configuração do contexto de criptografia para hashing de senhas
# Tinha apenas "bcrypt", agora inclui "argon2" como esquema padrão
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")



#-----------------------------------------------------------------------------------------------
# Funções relacionadas a tokens JWT e segurança de senhas
#-----------------------------------------------------------------------------------------------

#Função definida para criar um token de acesso JWT
def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    if settings.SECRET_KEY is None:
        raise ValueError("SECRET_KEY não está definido nas configurações.")
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Função definida para verificar se uma senha em texto  corresponde a uma senha hasheada
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Função definida para criar o hash de uma senha
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

#-----------------------------------------------------------------------------------------------