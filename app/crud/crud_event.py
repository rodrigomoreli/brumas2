# app/crud/crud_event.py

"""
Operações CRUD para eventos, despesas e degustações.

Define funções para manipulação de dados relacionados a eventos e suas
entidades associadas, utilizando SQLAlchemy e os schemas da aplicação.
"""

from sqlalchemy.orm import Session, joinedload
from app.models import event as models_event
from app.models import user as models_user
from app.schemas import event as schemas_event
from typing import Optional


def get_evento(db: Session, evento_id: int) -> models_event.Evento | None:
    """Busca um evento pelo ID, com todos os relacionamentos carregados."""
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
            joinedload(models_event.Evento.despesas),
        )
        .filter(models_event.Evento.id == evento_id)
        .first()
    )


def get_multi_eventos(
    db: Session,
    *,
    current_user: models_user.User,
    skip: int = 0,
    limit: int = 100,
    id_cliente: Optional[int] = None,
) -> list[models_event.Evento]:
    """Retorna uma lista de eventos com filtros e paginação."""
    query = db.query(models_event.Evento).options(
        joinedload(models_event.Evento.cliente),
        joinedload(models_event.Evento.local_evento),
        joinedload(models_event.Evento.buffet),
    )

    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    if id_cliente:
        query = query.filter(models_event.Evento.id_cliente == id_cliente)

    return query.offset(skip).limit(limit).all()


def create_evento(
    db: Session,
    *,
    evento_in: schemas_event.EventoCreate,
    user_id: int,
) -> models_event.Evento:
    """Cria um novo evento associado ao usuário criador."""
    evento_data = evento_in.model_dump(exclude={"venda"})
    db_evento = models_event.Evento(**evento_data, id_usuario_criador=user_id)

    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento


def delete_evento(
    db: Session,
    *,
    evento_obj: models_event.Evento,
) -> None:
    """Remove um evento do banco de dados."""
    db.delete(evento_obj)
    db.commit()


def add_despesa_to_evento(
    db: Session,
    *,
    evento_id: int,
    despesa_in: schemas_event.DespesaCreate,
    user_id: int,
) -> models_event.Despesa:
    """Adiciona uma despesa a um evento."""
    despesa_data = despesa_in.model_dump()
    db_obj = models_event.Despesa(
        **despesa_data,
        id_evento=evento_id,
        id_usuario_criador=user_id,
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_despesa(
    db: Session,
    *,
    despesa_obj: models_event.Despesa,
    despesa_in: schemas_event.DespesaUpdate,
) -> models_event.Despesa:
    """Atualiza os dados de uma despesa."""
    update_data = despesa_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(despesa_obj, field, value)

    db.add(despesa_obj)
    db.commit()
    db.refresh(despesa_obj)
    return despesa_obj


def delete_despesa(
    db: Session,
    *,
    despesa_obj: models_event.Despesa,
) -> None:
    """Remove uma despesa do banco de dados."""
    db.delete(despesa_obj)
    db.commit()


def add_degustacao_to_evento(
    db: Session,
    *,
    evento_id: int,
    degustacao_in: schemas_event.DegustacaoCreate,
    user_id: int,
) -> models_event.Degustacao:
    """Adiciona uma degustação a um evento."""
    degustacao_data = degustacao_in.model_dump()
    db_obj = models_event.Degustacao(
        **degustacao_data,
        id_evento=evento_id,
        id_usuario_criador=user_id,
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_degustacao(
    db: Session,
    *,
    degustacao_obj: models_event.Degustacao,
    degustacao_in: schemas_event.DegustacaoUpdate,
) -> models_event.Degustacao:
    """Atualiza os dados de uma degustação."""
    update_data = degustacao_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(degustacao_obj, field, value)

    db.add(degustacao_obj)
    db.commit()
    db.refresh(degustacao_obj)
    return degustacao_obj


def delete_degustacao(
    db: Session,
    *,
    degustacao_obj: models_event.Degustacao,
) -> None:
    """Remove uma degustação do banco de dados."""
    db.delete(degustacao_obj)
    db.commit()
