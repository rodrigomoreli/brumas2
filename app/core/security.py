# app/core/security.py

"""
Funções de segurança da aplicação.

Este módulo fornece utilitários para autenticação e proteção de dados,
incluindo geração de tokens JWT e hashing seguro de senhas.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

# Inicializa o contexto de hashing com suporte a argon2 e bcrypt
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Gera um token JWT de acesso.

    Args:
        subject: Identificador do usuário (ex: ID ou e-mail).
        expires_delta: Tempo de expiração do token. Se omitido, usa o padrão.

    Returns:
        Token JWT assinado como string.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}

    if settings.SECRET_KEY is None:
        raise ValueError("SECRET_KEY não está definido nas configurações.")

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.

    Args:
        plain_password: Senha em texto plano.
        hashed_password: Hash da senha armazenada.

    Returns:
        True se a senha for válida, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera o hash seguro de uma senha.

    Args:
        password: Senha em texto plano.

    Returns:
        Hash da senha.
    """
    return pwd_context.hash(password)
