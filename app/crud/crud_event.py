# app/crud/crud_event.py

from sqlalchemy.orm import Session, joinedload
from app.models import event as models_event
from app.models import user as models_user
from app.models import dimension as models_dimension
from app.schemas import event as schemas_event
from typing import Optional

# ===================================================================
#                           CRUD PARA EVENTOS
# ===================================================================

# READ EVENTO POR ID (Já está correto)
def get_evento(db: Session, evento_id: int) -> models_event.Evento | None:
    return (
        db.query(models_event.Evento)
        .options(
            joinedload(models_event.Evento.cliente),
            joinedload(models_event.Evento.local_evento),
            joinedload(models_event.Evento.buffet),
            joinedload(models_event.Evento.tipo_evento),
            joinedload(models_event.Evento.cidade),
            joinedload(models_event.Evento.assessoria),
            joinedload(models_event.Evento.degustacoes),
            joinedload(models_event.Evento.despesas)
        )
        .filter(models_event.Evento.id == evento_id)
        .first()
    )

# --- FUNÇÃO get_multi_eventos CORRIGIDA ---
def get_multi_eventos(
    db: Session, 
    *, 
    current_user: models_user.User, 
    skip: int = 0, 
    limit: int = 100,
    id_cliente: Optional[int] = None
) -> list[models_event.Evento]:
    """
    Retorna uma lista de eventos, usando a mesma estratégia de 'joinedload'
    para carregar os relacionamentos necessários para o schema 'EventoPublic'.
    """
    # 1. Inicia a consulta base
    query = db.query(models_event.Evento).options(
        # Carrega os relacionamentos necessários para as hybrid_properties
        # que o schema EventoPublic usa (cliente_nome, local_evento_nome, etc.)
        joinedload(models_event.Evento.cliente),
        joinedload(models_event.Evento.local_evento),
        joinedload(models_event.Evento.buffet)
    )

    # 2. Aplica o filtro de permissão
    if current_user.perfil != 'administrativo':
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    # 3. Aplica filtros opcionais
    if id_cliente:
        query = query.filter(models_event.Evento.id_cliente == id_cliente)

    # 4. Aplica a paginação e retorna os resultados
    # Não precisamos mais do loop manual, o Pydantic e as hybrid_properties
    # farão todo o trabalho pesado para nós.
    return query.offset(skip).limit(limit).all()


# ... (O resto do seu arquivo continua exatamente o mesmo) ...

# CREATE EVENTO COM VENDA ASSOCIADA
def create_evento(db: Session, *, evento_in: schemas_event.EventoCreate, user_id: int) -> models_event.Evento:
    evento_data = evento_in.model_dump(exclude={'venda'})
    db_evento = models_event.Evento(
        **evento_data, 
        id_usuario_criador=user_id
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

# DELETE EVENTO
def delete_evento(db: Session, *, evento_obj: models_event.Evento) -> None:
    db.delete(evento_obj)
    db.commit()
    return

# ===================================================================
#                           CRUD PARA DESPESAS
# ===================================================================

# CREATE DESPESA
def add_despesa_to_evento(
        db: Session, 
        *, 
        evento_id: int, 
        despesa_in: schemas_event.DespesaCreate, 
        user_id: int
) -> models_event.Despesa:
    despesa_data = despesa_in.model_dump()
    db_obj = models_event.Despesa(
        **despesa_data, 
        id_evento=evento_id, 
        id_usuario_criador=user_id
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# UPDATE DESPESA
def update_despesa(
        db: Session, 
        *, despesa_obj: models_event.Despesa, 
        despesa_in: schemas_event.DespesaUpdate
) -> models_event.Despesa:
    # 1. Converte o schema para um dicionário, pegando apenas os campos enviados.
    update_data = despesa_in.model_dump(exclude_unset=True)

    # 2. Itera sobre os dados e os aplica dinamicamente ao objeto do banco.
    for field, value in update_data.items():
        setattr(despesa_obj, field, value)

    # 3. Salva as mudanças no banco de dados.
    db.add(despesa_obj)
    db.commit()
    db.refresh(despesa_obj)
    
    return despesa_obj

# DELETE DESPESA
def delete_despesa(
        db: Session, 
        *, 
        despesa_obj: models_event.Despesa
) -> None:
    db.delete(despesa_obj)
    db.commit()
    return  


# ===================================================================
#                           CRUD PARA DEGUSTAÇÕES
# ===================================================================

# CREATE DEGUSTAÇÃO
def add_degustacao_to_evento(
        db: Session, 
        *, 
        evento_id: int, 
        degustacao_in: schemas_event.DegustacaoCreate, 
        user_id: int
) -> models_event.Degustacao:
    degustacao_data = degustacao_in.model_dump()
    db_obj = models_event.Degustacao(
        **degustacao_data, 
        id_evento=evento_id, 
        id_usuario_criador=user_id
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj

# UPDATE DEGUSTAÇÃO
def update_degustacao(
        db: Session, 
        *, 
        degustacao_obj: models_event.Degustacao, 
        degustacao_in: schemas_event.DegustacaoUpdate
) -> models_event.Degustacao:
    # Converte o schema Pydantic para um dicionário.
    # exclude_unset=True é crucial: ele garante que apenas os campos que o usuário
    # realmente enviou na requisição serão incluídos no dicionário.
    # Isso nos permite fazer atualizações parciais (PATCH).
    update_data = degustacao_in.model_dump(exclude_unset=True)

    # Itera sobre os dados de atualização e os aplica ao objeto do banco
    for field, value in update_data.items():
        setattr(degustacao_obj, field, value)

    # Adiciona o objeto modificado à sessão e commita a transação
    db.add(degustacao_obj)
    db.commit()
    db.refresh(degustacao_obj)
    
    return degustacao_obj

# DELETE DEGUSTAÇÃO
def delete_degustacao(
        db: Session, 
        *, 
        degustacao_obj: models_event.Degustacao
) -> None:
    db.delete(degustacao_obj)
    db.commit()
    
    return
