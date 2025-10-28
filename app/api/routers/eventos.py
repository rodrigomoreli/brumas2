# app/api/routers/eventos.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional

# Importações do seu projeto
from app.api import deps
from app.crud import crud_event
from app.schemas import event as schemas_event
from app.models import user as models_user

router = APIRouter()

# =============================================================================================================
#                           ROTA EVENTO
# =============================================================================================================

# CREATE EVENTO COM VENDA ASSOCIADA
@router.post("/", response_model=schemas_event.Evento, status_code=status.HTTP_201_CREATED)
def create_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_in: schemas_event.EventoCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    evento = crud_event.create_evento(db=db, evento_in=evento_in, user_id=current_user.id)
    return evento

# READ EVENTO POR ID
@router.get("/{evento_id}/", response_model=schemas_event.EventoDetail) # <<< A MUDANÇA ESTÁ AQUI
def read_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    """
    Recupera os detalhes completos de um evento.
    Usa o schema 'EventoDetail' para incluir os nomes dos relacionamentos.
    """
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # REGRA DE NEGÓCIO: Usuário operacional só pode ver evento que ele criou.
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para ver este evento")
    
    return evento

# READ TODOS OS EVENTOS COM BASE EM PERMISSOES, FILTROS E PAGINACAO
@router.get("/", response_model=List[schemas_event.EventoPublic])
def read_eventos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    id_cliente: Optional[int] = None,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    """
    Recupera a lista de eventos para os cards.
    Usa o schema 'EventoPublic', que é mais leve.
    """
    eventos = crud_event.get_multi_eventos(
        db=db, 
        current_user=current_user, 
        skip=skip, 
        limit=limit, 
        id_cliente=id_cliente
    )
    return eventos  

# DELETE EVENTO
@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com id {evento_id} não encontrado.",
        )
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este evento")
    
    crud_event.delete_evento(db=db, evento_obj=evento)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# =============================================================================================================
#                           ROTA DESPESAS
# =============================================================================================================

# CREATE DESPESA PARA UM EVENTO
@router.post("/{evento_id}/despesas", response_model=schemas_event.Despesa, status_code=status.HTTP_201_CREATED)
def add_despesa_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_in: schemas_event.DespesaCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    # 1. Validação de Existência: O evento existe?
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # 2. Validação de Permissão: O usuário pode modificar este evento?
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para modificar este evento")

    # 3. Execução: Se tudo estiver OK, chama a função CRUD para criar a despesa
    despesa = crud_event.add_despesa_to_evento(db=db, evento_id=evento_id, despesa_in=despesa_in, user_id=current_user.id)
    return despesa

# UPDATE DESPESA PARA UM EVENTO
@router.put("/{evento_id}/despesas/{despesa_id}", response_model=schemas_event.Despesa)
def update_despesa_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_id: int,
    despesa_in: schemas_event.DespesaUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    # 1. Validação de Existência do Evento "Pai"
    #    (Esta lógica é idêntica à dos endpoints de degustação)
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com id {evento_id} não encontrado.",
        )

    # 2. Validação de Permissão
    #    (Esta lógica é idêntica à dos endpoints de degustação)
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para modificar este evento")

    # 3. Encontra a despesa específica dentro do evento
    #    (Aqui usamos a relação 'evento.despesas' que o SQLAlchemy nos dá)
    despesa_obj = None
    for despesa in evento.despesas:
        if despesa.id == despesa_id:
            despesa_obj = despesa
            break
    
    if not despesa_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Despesa com id {despesa_id} não encontrada neste evento.",
        )

    # 4. Execução: Chama a função do CRUD que acabamos de criar
    updated_despesa = crud_event.update_despesa(db=db, despesa_obj=despesa_obj, despesa_in=despesa_in)
    
    return updated_despesa

# DELETE DESPESA PARA UM EVENTO
@router.delete("/{evento_id}/despesas/{despesa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_despesa_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    # 1. Validação de Existência do Evento "Pai"
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com id {evento_id} não encontrado.",
        )

    # 2. Validação de Permissão
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para modificar este evento")

    # 3. Encontra a despesa específica dentro do evento
    despesa_obj = None
    for despesa in evento.despesas:
        if despesa.id == despesa_id:
            despesa_obj = despesa
            break
    
    if not despesa_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Despesa com id {despesa_id} não encontrada neste evento.",
        )

    # 4. Execução: Chama a função do CRUD para deletar
    crud_event.delete_despesa(db=db, despesa_obj=despesa_obj)
    
    # 5. Retorno: Envia uma resposta HTTP 204 (Sucesso, Sem Conteúdo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# =============================================================================================================
#                       ROTA DEGUSTAÇÕES
# =============================================================================================================

# CREATE DEGUSTAÇÃO PARA UM EVENTO
@router.post("/{evento_id}/degustacoes", response_model=schemas_event.Degustacao, status_code=status.HTTP_201_CREATED)
def add_degustacao_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_in: schemas_event.DegustacaoCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    # 1. Validação de Existência: O evento existe?
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # 2. Validação de Permissão: O usuário pode modificar este evento?
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para modificar este evento")

    # 3. Execução: Se tudo estiver OK, chama a função CRUD para criar a degustação
    degustacao = crud_event.add_degustacao_to_evento(db=db, evento_id=evento_id, degustacao_in=degustacao_in, user_id=current_user.id)
    return degustacao

# UPDATE DEGUSTAÇÃO PARA UM EVENTO
@router.put("/{evento_id}/degustacoes/{degustacao_id}", response_model=schemas_event.Degustacao)
def update_degustacao_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_id: int,
    degustacao_in: schemas_event.DegustacaoUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    # 1. Verifica se o evento "pai" existe
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com id {evento_id} não encontrado.",
        )

    # 2. Procura a degustação específica dentro da lista de degustações do evento
    #    Para garantir que uma degustação que REALMENTE pertence a este evento.
    degustacao_obj = None
    for degustacao in evento.degustacoes:
        if degustacao.id == degustacao_id:
            degustacao_obj = degustacao
            break
    
    if not degustacao_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Degustação com id {degustacao_id} não encontrada neste evento.",
        )

    # 3. Se encontrou, chama a função do CRUD para aplicar as atualizações
    updated_degustacao = crud_event.update_degustacao(
        db=db, 
        degustacao_obj=degustacao_obj, 
        degustacao_in=degustacao_in
    )
    
    return updated_degustacao

# DELETE DEGUSTAÇÃO PARA UM EVENTO
@router.delete("/eventos/{evento_id}/degustacoes/{degustacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_degustacao_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user)
):
    # 1. Validação de Existência do Evento "Pai"
    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento com id {evento_id} não encontrado.",
        )

    # 2. Validação de Permissão (o usuário pode mexer neste evento?)
    if current_user.perfil != 'administrativo' and evento.id_usuario_criador != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para modificar este evento")

    # 3. Encontra a degustação específica dentro do evento
    degustacao_obj = None
    for degustacao in evento.degustacoes:
        if degustacao.id == degustacao_id:
            degustacao_obj = degustacao
            break
    
    if not degustacao_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Degustação com id {degustacao_id} não encontrada neste evento.",
        )

    # 4. Execução: Se tudo estiver OK, chama a função do CRUD para deletar
    crud_event.delete_degustacao(db=db, degustacao_obj=degustacao_obj)
    
    # Retorna uma resposta vazia com status 204, indicando sucesso na exclusão.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
