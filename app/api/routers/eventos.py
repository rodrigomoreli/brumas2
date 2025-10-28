# app/api/routers/eventos.py
"""
Rotas da API para gerenciamento de eventos, despesas e degustações.
Todas as operações são restritas a usuários com perfil operacional
ou administrativo.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.crud import crud_event
from app.schemas import event as schemas_event
from app.models import user as models_user

router = APIRouter()


@router.post(
    "/", response_model=schemas_event.Evento, status_code=status.HTTP_201_CREATED
)
def create_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_in: schemas_event.EventoCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Cria um novo evento."""
    return crud_event.create_evento(db=db, evento_in=evento_in, user_id=current_user.id)


@router.get("/{evento_id}/", response_model=schemas_event.EventoDetail)
def read_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Retorna os detalhes de um evento específico."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para ver este evento"
        )

    return evento


@router.get("/", response_model=List[schemas_event.EventoPublic])
def read_eventos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    id_cliente: Optional[int] = None,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Lista eventos visíveis ao usuário atual."""
    return crud_event.get_multi_eventos(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        id_cliente=id_cliente,
    )


@router.patch("/{evento_id}", response_model=schemas_event.Evento)
def update_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    evento_in: schemas_event.EventoUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Atualiza os dados de um evento existente."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=404, detail=f"Evento com id {evento_id} não encontrado."
        )

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para modificar este evento"
        )

    return crud_event.update_evento(db=db, evento_obj=evento, evento_in=evento_in)


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Remove um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=404, detail=f"Evento com id {evento_id} não encontrado."
        )

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para deletar este evento"
        )

    crud_event.delete_evento(db=db, evento_obj=evento)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{evento_id}/despesas",
    response_model=schemas_event.Despesa,
    status_code=status.HTTP_201_CREATED,
)
def add_despesa_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_in: schemas_event.DespesaCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Adiciona uma despesa a um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para modificar este evento"
        )

    return crud_event.add_despesa_to_evento(
        db=db, evento_id=evento_id, despesa_in=despesa_in, user_id=current_user.id
    )


@router.patch(
    "/{evento_id}/despesas/{despesa_id}", response_model=schemas_event.Despesa
)
def update_despesa_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_id: int,
    despesa_in: schemas_event.DespesaUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Atualiza uma despesa de um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=404, detail=f"Evento com id {evento_id} não encontrado."
        )

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para modificar este evento"
        )

    despesa_obj = next((d for d in evento.despesas if d.id == despesa_id), None)
    if not despesa_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Despesa com id {despesa_id} não encontrada neste evento.",
        )

    return crud_event.update_despesa(
        db=db, despesa_obj=despesa_obj, despesa_in=despesa_in
    )


@router.delete(
    "/{evento_id}/despesas/{despesa_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_despesa_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Remove uma despesa de um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=404, detail=f"Evento com id {evento_id} não encontrado."
        )

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para modificar este evento"
        )

    despesa_obj = next((d for d in evento.despesas if d.id == despesa_id), None)
    if not despesa_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Despesa com id {despesa_id} não encontrada neste evento.",
        )

    crud_event.delete_despesa(db=db, despesa_obj=despesa_obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{evento_id}/degustacoes",
    response_model=schemas_event.Degustacao,
    status_code=status.HTTP_201_CREATED,
)
def add_degustacao_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_in: schemas_event.DegustacaoCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Adiciona uma degustação a um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para modificar este evento"
        )

    return crud_event.add_degustacao_to_evento(
        db=db, evento_id=evento_id, degustacao_in=degustacao_in, user_id=current_user.id
    )


@router.patch(
    "/{evento_id}/degustacoes/{degustacao_id}", response_model=schemas_event.Degustacao
)
def update_degustacao_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_id: int,
    degustacao_in: schemas_event.DegustacaoUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Atualiza uma degustação de um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=404, detail=f"Evento com id {evento_id} não encontrado."
        )

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para modificar este evento"
        )

    degustacao_obj = next(
        (d for d in evento.degustacoes if d.id == degustacao_id), None
    )
    if not degustacao_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Degustação com id {degustacao_id} não encontrada neste evento.",
        )

    return crud_event.update_degustacao(
        db=db, degustacao_obj=degustacao_obj, degustacao_in=degustacao_in
    )


@router.delete(
    "/{evento_id}/degustacoes/{degustacao_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_degustacao_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Remove uma degustação de um evento."""
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com id {evento_id} não encontrado.",
        )

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para modificar este evento",
        )

    degustacao_obj = next(
        (d for d in evento.degustacoes if d.id == degustacao_id),
        None,
    )
    if not degustacao_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Degustação com id {degustacao_id} não encontrada neste evento.",
        )

    crud_event.delete_degustacao(db=db, degustacao_obj=degustacao_obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
