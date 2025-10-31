# app/crud/crud_event.py

"""
Operações CRUD para eventos, despesas e degustações.
Define funções para manipulação de dados relacionados a eventos e suas
entidades associadas, utilizando SQLAlchemy e os schemas da aplicação.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from fastapi import HTTPException, status
from app.models import event as models_event
from app.models import user as models_user
from app.models import dimension as models_dimension
from app.schemas import event as schemas_event
from typing import Optional
from datetime import date


def validate_evento_relationships(db: Session, evento_data: dict) -> None:
    """
    Valida se todos os IDs de relacionamentos existem no banco.
    Levanta HTTPException se algum ID for inválido.
    """
    # Validar cliente (obrigatório)
    if "id_cliente" in evento_data and evento_data["id_cliente"]:
        cliente = (
            db.query(models_dimension.Cliente)
            .filter(models_dimension.Cliente.id == evento_data["id_cliente"])
            .first()
        )
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente com id {evento_data['id_cliente']} não encontrado.",
            )

    # Validar local_evento (obrigatório)
    if "id_local_evento" in evento_data and evento_data["id_local_evento"]:
        local = (
            db.query(models_dimension.LocalEvento)
            .filter(models_dimension.LocalEvento.id == evento_data["id_local_evento"])
            .first()
        )
        if not local:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Local de evento com id {evento_data['id_local_evento']} não encontrado.",
            )

    # Validar tipo_evento (opcional)
    if "id_tipo_evento" in evento_data and evento_data["id_tipo_evento"]:
        tipo = (
            db.query(models_dimension.TipoEvento)
            .filter(models_dimension.TipoEvento.id == evento_data["id_tipo_evento"])
            .first()
        )
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de evento com id {evento_data['id_tipo_evento']} não encontrado.",
            )

    # Validar cidade (opcional)
    if "id_cidade" in evento_data and evento_data["id_cidade"]:
        cidade = (
            db.query(models_dimension.Cidade)
            .filter(models_dimension.Cidade.id == evento_data["id_cidade"])
            .first()
        )
        if not cidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cidade com id {evento_data['id_cidade']} não encontrada.",
            )

    # Validar assessoria (opcional)
    if "id_assessoria" in evento_data and evento_data["id_assessoria"]:
        assessoria = (
            db.query(models_dimension.Assessoria)
            .filter(models_dimension.Assessoria.id == evento_data["id_assessoria"])
            .first()
        )
        if not assessoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessoria com id {evento_data['id_assessoria']} não encontrada.",
            )

    # Validar buffet (opcional)
    if "id_buffet" in evento_data and evento_data["id_buffet"]:
        buffet = (
            db.query(models_dimension.Buffet)
            .filter(models_dimension.Buffet.id == evento_data["id_buffet"])
            .first()
        )
        if not buffet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Buffet com id {evento_data['id_buffet']} não encontrado.",
            )


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
            joinedload(models_event.Evento.usuario_criador),
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
    status_evento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    id_cidade: Optional[int] = None,
    id_buffet: Optional[int] = None,
    order_by: str = "data_evento",
    order_direction: str = "desc",
) -> list[models_event.Evento]:
    """
    Retorna uma lista de eventos com filtros avançados e ordenação.

    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros a retornar
        id_cliente: Filtrar por cliente específico
        status_evento: Filtrar por status (Orçamento, Confirmado, etc)
        data_inicio: Filtrar eventos a partir desta data
        data_fim: Filtrar eventos até esta data
        id_cidade: Filtrar por cidade
        id_buffet: Filtrar por buffet
        order_by: Campo para ordenação (data_evento, created_at, vlr_total_contrato)
        order_direction: Direção da ordenação (asc ou desc)

    Returns:
        Lista de eventos filtrados e ordenados
    """
    query = db.query(models_event.Evento).options(
        joinedload(models_event.Evento.cliente),
        joinedload(models_event.Evento.local_evento),
        joinedload(models_event.Evento.buffet),
        joinedload(models_event.Evento.tipo_evento),
        joinedload(models_event.Evento.cidade),
    )

    # Filtro de permissão: usuários não-admin só veem seus próprios eventos
    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    # Aplicar filtros
    if id_cliente:
        query = query.filter(models_event.Evento.id_cliente == id_cliente)

    if status_evento:
        query = query.filter(models_event.Evento.status_evento == status_evento)

    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)

    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    if id_cidade:
        query = query.filter(models_event.Evento.id_cidade == id_cidade)

    if id_buffet:
        query = query.filter(models_event.Evento.id_buffet == id_buffet)

    # Aplicar ordenação
    valid_order_fields = [
        "data_evento",
        "created_at",
        "updated_at",
        "vlr_total_contrato",
        "qtde_convidados_prevista",
        "status_evento",
    ]

    if order_by not in valid_order_fields:
        order_by = "data_evento"  # Default seguro

    order_column = getattr(models_event.Evento, order_by)

    if order_direction.lower() == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))

    return query.offset(skip).limit(limit).all()


def count_eventos(
    db: Session,
    *,
    current_user: models_user.User,
    id_cliente: Optional[int] = None,
    status_evento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    id_cidade: Optional[int] = None,
    id_buffet: Optional[int] = None,
) -> int:
    """
    Conta o total de eventos com os filtros aplicados.
    Usado para calcular paginação.
    """
    query = db.query(models_event.Evento)

    # Filtro de permissão
    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    # Aplicar mesmos filtros
    if id_cliente:
        query = query.filter(models_event.Evento.id_cliente == id_cliente)

    if status_evento:
        query = query.filter(models_event.Evento.status_evento == status_evento)

    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)

    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    if id_cidade:
        query = query.filter(models_event.Evento.id_cidade == id_cidade)

    if id_buffet:
        query = query.filter(models_event.Evento.id_buffet == id_buffet)

    return query.count()


def create_evento(
    db: Session,
    *,
    evento_in: schemas_event.EventoCreate,
    user_id: int,
) -> models_event.Evento:
    """Cria um novo evento associado ao usuário criador."""
    evento_data = evento_in.model_dump()

    # Validar relacionamentos antes de criar
    validate_evento_relationships(db, evento_data)

    db_evento = models_event.Evento(**evento_data, id_usuario_criador=user_id)
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento


def update_evento(
    db: Session,
    *,
    evento_obj: models_event.Evento,
    evento_in: schemas_event.EventoUpdate,
) -> models_event.Evento:
    """Atualiza os dados de um evento existente."""
    update_data = evento_in.model_dump(exclude_unset=True)

    # Validar relacionamentos antes de atualizar
    validate_evento_relationships(db, update_data)

    for field, value in update_data.items():
        setattr(evento_obj, field, value)

    db.add(evento_obj)
    db.commit()
    db.refresh(evento_obj)
    return evento_obj


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

    # Validar se o insumo existe
    insumo = (
        db.query(models_dimension.Insumo)
        .filter(models_dimension.Insumo.id == despesa_data["id_insumo"])
        .first()
    )
    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insumo com id {despesa_data['id_insumo']} não encontrado.",
        )

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

    # Validar se o insumo existe (se estiver sendo atualizado)
    if "id_insumo" in update_data and update_data["id_insumo"]:
        insumo = (
            db.query(models_dimension.Insumo)
            .filter(models_dimension.Insumo.id == update_data["id_insumo"])
            .first()
        )
        if not insumo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insumo com id {update_data['id_insumo']} não encontrado.",
            )

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


# ========== ✅ FUNÇÕES DE ESTATÍSTICAS ==========

from sqlalchemy import func, extract, case
from datetime import date as date_type
from typing import List, Dict, Any


def get_eventos_stats(
    db: Session,
    *,
    current_user: models_user.User,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
) -> Dict[str, Any]:
    """
    Retorna estatísticas gerais dos eventos.

    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        data_inicio: Data inicial para filtro
        data_fim: Data final para filtro

    Returns:
        Dicionário com estatísticas agregadas
    """
    # Query base
    query = db.query(models_event.Evento)

    # Filtro de permissão
    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    # Filtros de data
    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)
    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    # Total de eventos
    total_eventos = query.count()

    # Eventos por status
    eventos_orcamento = query.filter(
        models_event.Evento.status_evento == "Orçamento"
    ).count()
    eventos_confirmados = query.filter(
        models_event.Evento.status_evento == "Confirmado"
    ).count()
    eventos_realizados = query.filter(
        models_event.Evento.status_evento == "Realizado"
    ).count()
    eventos_cancelados = query.filter(
        models_event.Evento.status_evento == "Cancelado"
    ).count()

    # Valores totais
    valores = query.with_entities(
        func.coalesce(func.sum(models_event.Evento.vlr_total_contrato), 0).label(
            "total"
        ),
        func.coalesce(func.avg(models_event.Evento.vlr_total_contrato), 0).label(
            "media"
        ),
    ).first()

    valor_total_contratos = valores.total if valores else 0
    valor_medio_contrato = valores.media if valores else 0

    # Valor total de orçamentos
    valor_orcamentos = (
        query.filter(models_event.Evento.status_evento == "Orçamento")
        .with_entities(
            func.coalesce(func.sum(models_event.Evento.vlr_total_contrato), 0)
        )
        .scalar()
        or 0
    )

    # Valor total de confirmados
    valor_confirmados = (
        query.filter(models_event.Evento.status_evento == "Confirmado")
        .with_entities(
            func.coalesce(func.sum(models_event.Evento.vlr_total_contrato), 0)
        )
        .scalar()
        or 0
    )

    # Total de convidados
    convidados = query.with_entities(
        func.coalesce(func.sum(models_event.Evento.qtde_convidados_prevista), 0).label(
            "total"
        ),
        func.coalesce(func.avg(models_event.Evento.qtde_convidados_prevista), 0).label(
            "media"
        ),
    ).first()

    total_convidados = convidados.total if convidados else 0
    media_convidados = float(convidados.media) if convidados else 0.0

    # Total de despesas
    despesas_query = db.query(models_event.Despesa).join(models_event.Evento)
    if current_user.perfil != "administrativo":
        despesas_query = despesas_query.filter(
            models_event.Evento.id_usuario_criador == current_user.id
        )
    if data_inicio:
        despesas_query = despesas_query.filter(
            models_event.Evento.data_evento >= data_inicio
        )
    if data_fim:
        despesas_query = despesas_query.filter(
            models_event.Evento.data_evento <= data_fim
        )

    total_despesas = (
        despesas_query.with_entities(
            func.coalesce(func.sum(models_event.Despesa.vlr_total_pago), 0)
        ).scalar()
        or 0
    )

    # Total de degustações
    degustacoes_query = db.query(models_event.Degustacao).join(models_event.Evento)
    if current_user.perfil != "administrativo":
        degustacoes_query = degustacoes_query.filter(
            models_event.Evento.id_usuario_criador == current_user.id
        )
    if data_inicio:
        degustacoes_query = degustacoes_query.filter(
            models_event.Evento.data_evento >= data_inicio
        )
    if data_fim:
        degustacoes_query = degustacoes_query.filter(
            models_event.Evento.data_evento <= data_fim
        )

    total_degustacoes = degustacoes_query.count()
    valor_degustacoes = (
        degustacoes_query.with_entities(
            func.coalesce(func.sum(models_event.Degustacao.vlr_degustacao), 0)
        ).scalar()
        or 0
    )

    return {
        "total_eventos": total_eventos,
        "eventos_orcamento": eventos_orcamento,
        "eventos_confirmados": eventos_confirmados,
        "eventos_realizados": eventos_realizados,
        "eventos_cancelados": eventos_cancelados,
        "valor_total_contratos": valor_total_contratos,
        "valor_medio_contrato": valor_medio_contrato,
        "valor_total_orcamentos": valor_orcamentos,
        "valor_total_confirmados": valor_confirmados,
        "total_convidados_previsto": total_convidados,
        "media_convidados_por_evento": media_convidados,
        "total_despesas": total_despesas,
        "total_degustacoes": total_degustacoes,
        "valor_total_degustacoes": valor_degustacoes,
    }


def get_eventos_por_mes(
    db: Session,
    *,
    current_user: models_user.User,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
) -> List[Dict[str, Any]]:
    """
    Retorna eventos agrupados por mês.
    """
    query = db.query(
        func.to_char(models_event.Evento.data_evento, "YYYY-MM").label("mes"),
        func.count(models_event.Evento.id).label("total_eventos"),
        func.coalesce(func.sum(models_event.Evento.vlr_total_contrato), 0).label(
            "valor_total"
        ),
    )

    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)
    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    query = query.group_by("mes").order_by("mes")

    results = query.all()

    return [
        {
            "mes": r.mes,
            "total_eventos": r.total_eventos,
            "valor_total": r.valor_total,
        }
        for r in results
    ]


def get_eventos_por_status(
    db: Session,
    *,
    current_user: models_user.User,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
) -> List[Dict[str, Any]]:
    """
    Retorna eventos agrupados por status.
    """
    query = db.query(
        models_event.Evento.status_evento.label("status"),
        func.count(models_event.Evento.id).label("total"),
        func.coalesce(func.sum(models_event.Evento.vlr_total_contrato), 0).label(
            "valor_total"
        ),
    )

    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)
    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    query = query.group_by("status")

    results = query.all()
    total_geral = sum(r.total for r in results)

    return [
        {
            "status": r.status,
            "total": r.total,
            "percentual": round(
                (r.total / total_geral * 100) if total_geral > 0 else 0, 2
            ),
            "valor_total": r.valor_total,
        }
        for r in results
    ]


def get_top_clientes(
    db: Session,
    *,
    current_user: models_user.User,
    limit: int = 10,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
) -> List[Dict[str, Any]]:
    """
    Retorna os top clientes por valor de contratos.
    """
    query = db.query(
        models_event.Evento.id_cliente,
        models_dimension.Cliente.nome.label("cliente_nome"),
        func.count(models_event.Evento.id).label("total_eventos"),
        func.coalesce(func.sum(models_event.Evento.vlr_total_contrato), 0).label(
            "valor_total"
        ),
    ).join(
        models_dimension.Cliente,
        models_event.Evento.id_cliente == models_dimension.Cliente.id,
    )

    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)
    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    query = (
        query.group_by(models_event.Evento.id_cliente, models_dimension.Cliente.nome)
        .order_by(desc(func.sum(models_event.Evento.vlr_total_contrato)))
        .limit(limit)
    )

    results = query.all()

    return [
        {
            "id_cliente": r.id_cliente,
            "cliente_nome": r.cliente_nome,
            "total_eventos": r.total_eventos,
            "valor_total": r.valor_total,
        }
        for r in results
    ]


def get_despesas_por_insumo(
    db: Session,
    *,
    current_user: models_user.User,
    limit: int = 10,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
) -> List[Dict[str, Any]]:
    """
    Retorna despesas agrupadas por insumo.
    """
    query = (
        db.query(
            models_event.Despesa.id_insumo,
            models_dimension.Insumo.descricao.label("insumo_descricao"),
            func.coalesce(func.sum(models_event.Despesa.quantidade), 0).label(
                "quantidade_total"
            ),
            func.coalesce(func.sum(models_event.Despesa.vlr_total_pago), 0).label(
                "valor_total"
            ),
            func.count(func.distinct(models_event.Despesa.id_evento)).label(
                "numero_eventos"
            ),
        )
        .join(
            models_dimension.Insumo,
            models_event.Despesa.id_insumo == models_dimension.Insumo.id,
        )
        .join(
            models_event.Evento,
            models_event.Despesa.id_evento == models_event.Evento.id,
        )
    )

    if current_user.perfil != "administrativo":
        query = query.filter(models_event.Evento.id_usuario_criador == current_user.id)

    if data_inicio:
        query = query.filter(models_event.Evento.data_evento >= data_inicio)
    if data_fim:
        query = query.filter(models_event.Evento.data_evento <= data_fim)

    query = (
        query.group_by(
            models_event.Despesa.id_insumo, models_dimension.Insumo.descricao
        )
        .order_by(desc(func.sum(models_event.Despesa.vlr_total_pago)))
        .limit(limit)
    )

    results = query.all()

    return [
        {
            "id_insumo": r.id_insumo,
            "insumo_descricao": r.insumo_descricao,
            "quantidade_total": r.quantidade_total,
            "valor_total": r.valor_total,
            "numero_eventos": r.numero_eventos,
        }
        for r in results
    ]
