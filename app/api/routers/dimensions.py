# app/api/routers/dimensions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.crud import crud_dimension
from app.schemas import dimension as schemas_dim
from app.models import user as models_user
import enum


# ===================================================================
# Criado de uma função para gerar routers CRUD genéricos
# ===================================================================

def create_crud_router(
    *,
    prefix: str,
    tags: List[str],
    crud_instance: Any,
    schema: Any,
    create_schema: Any,
    update_schema: Any
) -> APIRouter:
    
    router = APIRouter()

# --- ENDPOINT PARA CREATE GENERICO ---
    @router.post(
            "/", 
            response_model=schema, 
            status_code=status.HTTP_201_CREATED
    )

    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        item_in: create_schema,
        current_user: models_user.User = Depends(deps.get_current_active_user)
    ):
        return crud_instance.create(
            db=db, 
            obj_in=item_in, 
            user_id=current_user.id
        )

# --- ENDPOINT PARA READ LISTA GENERICA ---
    @router.get(
            "/", 
            response_model=List[schema]
    )

    def read_items(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models_user.User = Depends(deps.get_current_active_user)
    ):
        return crud_instance.get_multi(
            db=db, 
            skip=skip, 
            limit=limit
        )

# --- ENDPOINT PARA READ UM ITEM ESPECÍFICO ---
    @router.get(
            "/{item_id}", 
            response_model=schema
    )

    def read_item(
        *,
        db: Session = Depends(deps.get_db),
        item_id: int,
        current_user: models_user.User = Depends(deps.get_current_active_user)
    ):
        item = crud_instance.get(
            db=db, 
            id=item_id
        )

        if not item:
            raise HTTPException(
                status_code=404, 
                detail=f"{tags[0]} não encontrado"
            )
        
        # ensure we compare plain Python values (not SQLAlchemy expression objects)
        creator_id = getattr(item, "id_usuario_criador", None)
        if current_user.perfil != 'administrativo' and creator_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Você não tem permissão para ver este item"
            )

        return item

# --- ENDPOINT PARA ATUALIZAR UM ITEM ---
    @router.patch(
            "/{item_id}", 
            response_model=schema
    )

    def update_item(
        *,
        db: Session = Depends(deps.get_db),
        item_id: int,
        item_in: update_schema,
        current_user: models_user.User = Depends(deps.get_current_active_user)
    ):
        db_obj = crud_instance.get(
            db=db, 
            id=item_id
        )

        if not db_obj:
            raise HTTPException(
                status_code=404, 
                detail=f"{tags[0]} não encontrado"
            )
        
        creator_id = getattr(db_obj, "id_usuario_criador", None)
        if current_user.perfil != 'administrativo' and creator_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Você não tem permissão para modificar este item"
            )
            
        return crud_instance.update(
            db=db, 
            db_obj=db_obj, 
            obj_in=item_in
        )
    
# --- ENDPOINT PARA DELETAR UM ITEM ---
    @router.delete("/{item_id}", response_model=schema)
    def delete_item(
        *,
        db: Session = Depends(deps.get_db),
        item_id: int,
        current_user: models_user.User = Depends(deps.get_current_active_user)
    ):
        db_obj = crud_instance.get(db=db, id=item_id)
        if not db_obj:
            raise HTTPException(
                status_code=404, 
                detail=f"{tags[0]} não encontrado"
            )
        
        creator_id = getattr(db_obj, "id_usuario_criador", None)
        if current_user.perfil != 'administrativo' and creator_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Você não tem permissão para deletar este item"
            )
        
        deleted_item = crud_instance.remove(db=db, id=item_id)
        return deleted_item

# Adicionado um prefixo e uma tags ao router gerado
    final_router = APIRouter()
    
    final_router.include_router(
        router, 
        prefix=prefix, 
        tags=tags
    )

    return final_router


# ===================================================================
# GERANDO OS ENDPOINTS PARA CADA DIMENSÃO
# ===================================================================

# ROTA PRINCIPAL PARA AGRUPAR OS ENDPOINTS DE DIMENSÕES
router = APIRouter()

# ENDPOINTS PARA ASSESSORIA
router.include_router(create_crud_router(
    prefix="/assessorias",
    tags=["Assessorias"],
    crud_instance=crud_dimension.crud_assessoria,
    schema=schemas_dim.Assessoria,
    create_schema=schemas_dim.AssessoriaCreate,
    update_schema=schemas_dim.AssessoriaUpdate
))

# ENDPOINTS PARA BUFFETS
router.include_router(create_crud_router(
    prefix="/buffets",
    tags=["Buffets"],
    crud_instance=crud_dimension.crud_buffet,
    schema=schemas_dim.Buffet,
    create_schema=schemas_dim.BuffetCreate,
    update_schema=schemas_dim.BuffetUpdate
))

# ENDPOINTS PARA CIDADES
router.include_router(create_crud_router(
    prefix="/cidades",
    tags=["Cidades"],
    crud_instance=crud_dimension.crud_cidade,
    schema=schemas_dim.Cidade,
    create_schema=schemas_dim.CidadeCreate,
    update_schema=schemas_dim.CidadeUpdate
))

# ENDPOINTS PARA CLIENTES
router.include_router(create_crud_router(
    prefix="/clientes",
    tags=["Clientes"],
    crud_instance=crud_dimension.crud_cliente,
    schema=schemas_dim.Cliente,
    create_schema=schemas_dim.ClienteCreate,
    update_schema=schemas_dim.ClienteUpdate
))

# ENDPOINTS PARA INSUMOS
router.include_router(create_crud_router(
    prefix="/insumos",
    tags=["Insumos"],
    crud_instance=crud_dimension.crud_insumo,
    schema=schemas_dim.Insumo,
    create_schema=schemas_dim.InsumoCreate,
    update_schema=schemas_dim.InsumoUpdate
))

# ENDPOINTS PARA LOCAIS DE EVENTO
router.include_router(create_crud_router(
    prefix="/locais_evento",
    tags=["Locais de Evento"],
    crud_instance=crud_dimension.crud_local_evento,
    schema=schemas_dim.LocalEvento,
    create_schema=schemas_dim.LocalEventoCreate,
    update_schema=schemas_dim.LocalEventoUpdate
))

# ENDPOINTS PARA TIPOS DE EVENTO
router.include_router(create_crud_router(
    prefix="/tipos_eventos",
    tags=["Tipos de Evento"],
    crud_instance=crud_dimension.crud_tipo_evento,
    schema=schemas_dim.TipoEvento,
    create_schema=schemas_dim.TipoEventoCreate,
    update_schema=schemas_dim.TipoEventoUpdate
))
