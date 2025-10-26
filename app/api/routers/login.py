# app/api/routers/login.py
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

# Endpoint para login e obtenção de token de acesso
@router.post("/login/access-token", response_model=schemas_token.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    # 1. Busca o usuário pelo username (que vem no form_data)
    user = crud_user.get_user_by_username(db, username=form_data.username)
    
    # 2. Verifica se o usuário existe e se a senha está correta
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    # 3. Cria o token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
