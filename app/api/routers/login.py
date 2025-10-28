# app/api/routers/login.py

"""
Rota de autenticação da API.

Define o endpoint responsável por validar credenciais e gerar
o token JWT de acesso.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api import deps
from app.crud import crud_user
from app.core import security
from app.core.config import settings
from app.schemas import token as schemas_token

router = APIRouter()


@router.post("/login/access-token", response_model=schemas_token.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> schemas_token.Token:
    """
    Autentica o usuário e retorna um token JWT de acesso.
    """
    user = crud_user.get_user_by_username(db, username=form_data.username)

    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Usuário inativo",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
