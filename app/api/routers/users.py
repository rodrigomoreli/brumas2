from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.crud import crud_user
from app.schemas import user as schemas_user
from app.models import user as models_user


router = APIRouter()

# CREATE USUARIO - Apenas admin pode criar novos usuários
@router.post("/", response_model=schemas_user.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas_user.UserCreate,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user)
):

    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com este email no sistema.",
        )

    user = crud_user.create_user(db=db, user_in=user_in)
    return user

# READ USUARIOS - Apenas admin pode listar usuários
@router.get("/", response_model=List[schemas_user.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user)
):
  
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

# READ USUARIO POR ID - Apenas admin pode ver detalhes de um usuário específico
@router.get("/{user_id}", response_model=schemas_user.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models_user.User = Depends(deps.get_current_active_admin_user)
):
    # A dependência já garante que o usuário é admin.
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {user_id} não encontrado.",
        )
    return user

# UPDATE USUARIO POR ID - Apenas admin pode atualizar usuários
@router.put("/{user_id}", response_model=schemas_user.User)
def update_user_by_admin(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas_user.UserUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user)
):
    # 1. Busca o usuário que será atualizado no banco de dados
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {user_id} não encontrado.",
        )

    # 2. Chama a função do CRUD para aplicar as atualizações
    # A função 'update_user' que você já tem é perfeita para isso.
    updated_user = crud_user.update_user(db=db, db_user=user, user_in=user_in)
    
    return updated_user

# DELETE USUARIO POR ID - Apenas admin pode deletar usuários
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_admin(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_admin_user)
):
    # 1. Busca o usuário que será deletado
    user_to_delete = crud_user.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com id {user_id} não encontrado.",
        )

    # 2. Validação de Segurança: Impede a auto-exclusão
    if user_to_delete.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administradores não podem deletar a si mesmos.",
        )

    # 3. Chama a função do CRUD para deletar
    crud_user.delete_user(db=db, user_to_delete=user_to_delete)

    # 4. Retorna uma resposta de sucesso sem conteúdo
    return Response(status_code=status.HTTP_204_NO_CONTENT)

