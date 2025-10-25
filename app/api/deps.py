from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import SessionLocal
from app.core.config import settings
from app.models import user as models_user
from app.crud import crud_user
from app.schemas import token as schemas_token

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

def get_db() -> Generator:
    """
    Fornece uma sessão de banco de dados para um endpoint da API.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models_user.User:
    """
    Decodifica o token JWT para obter o ID do usuário e busca o usuário no banco.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas_token.TokenPayload(**payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não foi possível validar as credenciais",
        )
    user = crud_user.get_user(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

def get_current_active_user(
    current_user: models_user.User = Depends(get_current_user),
) -> models_user.User:
    """
    Verifica se o usuário obtido do token está ativo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

def get_current_active_admin_user(
    current_user: models_user.User = Depends(get_current_active_user),
) -> models_user.User:
    """
    Verifica se o usuário ativo tem perfil 'administrativo'.
    """
    if current_user.perfil != 'administrativo':
        raise HTTPException(
            status_code=403, detail="O usuário não tem privilégios suficientes"
        )
    return current_user

def get_current_active_operational_user(
    current_user: models_user.User = Depends(get_current_active_user),
) -> models_user.User:
    """
    Verifica se o usuário ativo tem perfil 'operacional' ou 'administrativo'.
    (Um admin pode fazer tudo que um operacional faz).
    """
    if current_user.perfil not in ['operacional', 'administrativo']:
        raise HTTPException(
            status_code=403, detail="O usuário não tem privilégios suficientes"
        )
    return current_user
