# app/api/routers/users.py

"""
Rotas da API para gerenciamento de usuários.

Todas as operações são restritas a usuários com perfil administrativo.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud import crud_user
from app.schemas import user as schemas_user
from app.models import user as models_user

router = APIRouter()


@router.get(
    "/me",
    response_model=schemas_user.User,
    summary="Buscar dados do usuário autenticado",
    description="Retorna os dados do usuário atualmente autenticado",
    responses={
        200: {"description": "Dados do usuário retornados com sucesso"},
        401: {"description": "Não autenticado"},
    },
)
def read_current_user(
    current_user: models_user.User = Depends(deps.get_current_active_user),
) -> schemas_user.User:
    """
    Retorna os dados do usuário autenticado.

    Qualquer usuário autenticado pode acessar seus próprios dados.
    Não requer permissões especiais.
    """
    return current_user


@router.post(
    "/",
    response_model=schemas_user.User,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas_user.UserCreate,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user),
) -> schemas_user.User:
    """Cria um novo usuário. Apenas administradores têm permissão."""
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com este email no sistema.",
        )
    return crud_user.create_user(db=db, user_in=user_in)


@router.get("/", response_model=List[schemas_user.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user),
) -> List[schemas_user.User]:
    """Lista todos os usuários. Apenas administradores têm permissão."""
    return crud_user.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas_user.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_admin_user),
) -> schemas_user.User:
    """Retorna os dados de um usuário específico pelo ID."""
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {user_id} não encontrado.",
        )
    return user


@router.put("/{user_id}", response_model=schemas_user.User)
def update_user_by_admin(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas_user.UserUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user),
) -> schemas_user.User:
    """Atualiza os dados de um usuário existente."""
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {user_id} não encontrado.",
        )
    return crud_user.update_user(db=db, db_user=user, user_in=user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_admin(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user),
) -> Response:
    """Remove um usuário do sistema. Admins não podem se auto-excluir."""
    user_to_delete = crud_user.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {user_id} não encontrado.",
        )
    if user_to_delete.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administradores não podem deletar a si mesmos.",
        )
    crud_user.delete_user(db=db, user_to_delete=user_to_delete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
