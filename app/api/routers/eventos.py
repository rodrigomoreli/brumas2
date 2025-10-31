# app/api/routers/eventos.py

"""
Rotas da API para gerenciamento de eventos, despesas e degustações.
Todas as operações são restritas a usuários com perfil operacional
ou administrativo.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date as date_type

from app.api import deps
from app.crud import crud_event
from app.schemas import event as schemas_event
from app.schemas.common import PaginatedResponse
from app.models import user as models_user
from app.core.logging import log_info, log_warning, log_error

router = APIRouter()


def validate_event_permission(
    evento, current_user: models_user.User, action: str = "modificar"
):
    """
    Valida se o usuário tem permissão para realizar ação no evento.
    """
    if not evento:
        log_warning(
            f"Tentativa de acesso a evento inexistente",
            extra={"user_id": current_user.id, "action": action},
        )
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if (
        current_user.perfil != "administrativo"
        and evento.id_usuario_criador != current_user.id
    ):
        log_warning(
            f"Tentativa de acesso não autorizado ao evento",
            extra={
                "user_id": current_user.id,
                "evento_id": evento.id,
                "action": action,
                "evento_owner": evento.id_usuario_criador,
            },
        )
        raise HTTPException(
            status_code=403, detail=f"Você não tem permissão para {action} este evento"
        )


# ========== ENDPOINTS DE EVENTOS ==========


@router.post(
    "/",
    response_model=schemas_event.Evento,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo evento",
    description="Cria um novo evento no sistema com validação de relacionamentos",
    responses={
        201: {"description": "Evento criado com sucesso"},
        400: {"description": "Dados inválidos"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão"},
        404: {"description": "Cliente ou local não encontrado"},
    },
)
def create_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_in: schemas_event.EventoCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Cria um novo evento."""
    try:
        log_info(
            "Iniciando criação de evento",
            extra={
                "user_id": current_user.id,
                "cliente_id": evento_in.id_cliente,
                "data_evento": str(evento_in.data_evento),
            },
        )

        evento = crud_event.create_evento(
            db=db, evento_in=evento_in, user_id=current_user.id
        )

        log_info(
            "Evento criado com sucesso",
            extra={
                "user_id": current_user.id,
                "evento_id": evento.id,
                "cliente_id": evento.id_cliente,
                "data_evento": str(evento.data_evento),
                "status": evento.status_evento,
            },
        )

        return evento

    except HTTPException as e:
        log_error(
            f"Erro ao criar evento: {e.detail}",
            extra={
                "user_id": current_user.id,
                "error_status": e.status_code,
                "error_detail": e.detail,
            },
        )
        raise
    except Exception as e:
        log_error(
            f"Erro inesperado ao criar evento: {str(e)}",
            extra={
                "user_id": current_user.id,
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Erro interno ao criar evento")


@router.get(
    "/{evento_id}/",
    response_model=schemas_event.EventoDetail,
    summary="Buscar evento por ID",
    description="Retorna todos os detalhes de um evento específico, incluindo despesas e degustações",
    responses={
        200: {"description": "Evento encontrado"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para ver este evento"},
        404: {"description": "Evento não encontrado"},
    },
)
def read_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Retorna os detalhes de um evento específico."""
    log_info(
        "Buscando detalhes do evento",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "ver")

    log_info(
        "Evento recuperado com sucesso",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "status": evento.status_evento,
        },
    )

    return evento


@router.get(
    "/",
    response_model=PaginatedResponse[schemas_event.EventoPublic],
    summary="Listar eventos com paginação",
    description="""
    Lista eventos com filtros avançados, ordenação e paginação estruturada.
    
    **Filtros disponíveis:**
    - `id_cliente`: Filtrar por cliente específico
    - `status_evento`: Filtrar por status (Orçamento, Confirmado, Realizado, Cancelado)
    - `data_inicio`: Eventos a partir desta data
    - `data_fim`: Eventos até esta data
    - `id_cidade`: Filtrar por cidade
    - `id_buffet`: Filtrar por buffet
    
    **Ordenação:**
    - `order_by`: Campo para ordenar (data_evento, created_at, vlr_total_contrato, qtde_convidados_prevista)
    - `order_direction`: Direção (asc = crescente, desc = decrescente)
    
    **Paginação:**
    - `page`: Número da página (começa em 1)
    - `page_size`: Quantidade de itens por página (máximo 100)
    
    **Exemplos:**
    - Primeira página: `?page=1&page_size=20`
    - Eventos confirmados: `?status_evento=Confirmado&page=1&page_size=20`
    - Eventos de dezembro ordenados por valor: `?data_inicio=2025-12-01&data_fim=2025-12-31&order_by=vlr_total_contrato&order_direction=desc&page=1&page_size=20`
    """,
    responses={
        200: {"description": "Lista de eventos retornada com sucesso"},
        401: {"description": "Não autenticado"},
    },
)
def read_eventos(
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1, description="Número da página (começa em 1)"),
    page_size: int = Query(
        20, ge=1, le=100, description="Quantidade de itens por página (máximo 100)"
    ),
    id_cliente: Optional[int] = Query(None, description="Filtrar por ID do cliente"),
    status_evento: Optional[str] = Query(
        None,
        description="Filtrar por status (Orçamento, Confirmado, Realizado, Cancelado)",
    ),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    id_cidade: Optional[int] = Query(None, description="Filtrar por ID da cidade"),
    id_buffet: Optional[int] = Query(None, description="Filtrar por ID do buffet"),
    order_by: str = Query(
        "data_evento",
        description="Campo para ordenação (data_evento, created_at, vlr_total_contrato)",
    ),
    order_direction: str = Query(
        "desc", regex="^(asc|desc)$", description="Direção da ordenação (asc ou desc)"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Lista eventos com paginação estruturada.

    Retorna um objeto com:
    - items: Lista de eventos da página
    - total: Total de eventos (considerando filtros)
    - page: Página atual
    - page_size: Tamanho da página
    - total_pages: Total de páginas
    - has_next: Se tem próxima página
    - has_previous: Se tem página anterior
    """
    log_info(
        "Listando eventos",
        extra={
            "user_id": current_user.id,
            "page": page,
            "page_size": page_size,
            "filters": {
                "id_cliente": id_cliente,
                "status_evento": status_evento,
                "data_inicio": str(data_inicio) if data_inicio else None,
                "data_fim": str(data_fim) if data_fim else None,
                "id_cidade": id_cidade,
                "id_buffet": id_buffet,
            },
            "order_by": order_by,
            "order_direction": order_direction,
        },
    )

    skip = (page - 1) * page_size

    eventos = crud_event.get_multi_eventos(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=page_size,
        id_cliente=id_cliente,
        status_evento=status_evento,
        data_inicio=data_inicio,
        data_fim=data_fim,
        id_cidade=id_cidade,
        id_buffet=id_buffet,
        order_by=order_by,
        order_direction=order_direction,
    )

    total = crud_event.count_eventos(
        db=db,
        current_user=current_user,
        id_cliente=id_cliente,
        status_evento=status_evento,
        data_inicio=data_inicio,
        data_fim=data_fim,
        id_cidade=id_cidade,
        id_buffet=id_buffet,
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    log_info(
        "Eventos listados com sucesso",
        extra={
            "user_id": current_user.id,
            "total_found": total,
            "page": page,
            "total_pages": total_pages,
            "items_returned": len(eventos),
        },
    )

    return PaginatedResponse(
        items=eventos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )


@router.patch(
    "/{evento_id}",
    response_model=schemas_event.Evento,
    summary="Atualizar evento",
    description="Atualiza os dados de um evento existente (atualização parcial)",
    responses={
        200: {"description": "Evento atualizado com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para modificar este evento"},
        404: {"description": "Evento não encontrado"},
    },
)
def update_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    evento_in: schemas_event.EventoUpdate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Atualiza os dados de um evento existente."""
    log_info(
        "Iniciando atualização de evento",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "fields_to_update": list(evento_in.model_dump(exclude_unset=True).keys()),
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    evento_updated = crud_event.update_evento(
        db=db, evento_obj=evento, evento_in=evento_in
    )

    log_info(
        "Evento atualizado com sucesso",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "updated_fields": list(evento_in.model_dump(exclude_unset=True).keys()),
        },
    )

    return evento_updated


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar evento",
    description="Remove um evento do sistema (operação irreversível)",
    responses={
        204: {"description": "Evento deletado com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para deletar este evento"},
        404: {"description": "Evento não encontrado"},
    },
)
def delete_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Remove um evento."""
    log_warning(
        "Iniciando deleção de evento",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "deletar")

    # Registrar informações antes de deletar
    log_info(
        "Evento deletado",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "cliente_id": evento.id_cliente,
            "data_evento": str(evento.data_evento),
            "status": evento.status_evento,
        },
    )

    crud_event.delete_evento(db=db, evento_obj=evento)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ========== ENDPOINTS DE ESTATÍSTICAS E DASHBOARD ==========


@router.get(
    "/stats/geral",
    response_model=schemas_event.EventoStats,
    summary="Estatísticas gerais de eventos",
    description="""
    Retorna estatísticas agregadas dos eventos.
    
    **Métricas incluídas:**
    - Total de eventos por status
    - Valores totais e médios de contratos
    - Total de convidados previstos
    - Total de despesas e degustações
    
    **Filtros opcionais:**
    - `data_inicio`: Filtrar eventos a partir desta data
    - `data_fim`: Filtrar eventos até esta data
    
    **Exemplos:**
    - Estatísticas do ano: `?data_inicio=2025-01-01&data_fim=2025-12-31`
    - Estatísticas do mês: `?data_inicio=2025-12-01&data_fim=2025-12-31`
    """,
    responses={
        200: {"description": "Estatísticas retornadas com sucesso"},
        401: {"description": "Não autenticado"},
    },
)
def get_eventos_statistics(
    db: Session = Depends(deps.get_db),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Retorna estatísticas gerais dos eventos.
    """
    log_info(
        "Buscando estatísticas de eventos",
        extra={
            "user_id": current_user.id,
            "data_inicio": str(data_inicio) if data_inicio else None,
            "data_fim": str(data_fim) if data_fim else None,
        },
    )

    stats = crud_event.get_eventos_stats(
        db=db,
        current_user=current_user,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    log_info(
        "Estatísticas recuperadas com sucesso",
        extra={
            "user_id": current_user.id,
            "total_eventos": stats["total_eventos"],
            "valor_total": float(stats["valor_total_contratos"]),
        },
    )

    return stats


@router.get(
    "/stats/por-mes",
    response_model=List[schemas_event.EventosPorMes],
    summary="Eventos agrupados por mês",
    description="""
    Retorna eventos agrupados por mês com totais e valores.
    
    Útil para gráficos de linha mostrando evolução temporal.
    
    **Filtros opcionais:**
    - `data_inicio`: Filtrar eventos a partir desta data
    - `data_fim`: Filtrar eventos até esta data
    """,
)
def get_eventos_por_mes(
    db: Session = Depends(deps.get_db),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Retorna eventos agrupados por mês.
    """
    log_info("Buscando eventos por mês", extra={"user_id": current_user.id})

    return crud_event.get_eventos_por_mes(
        db=db,
        current_user=current_user,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get(
    "/stats/por-status",
    response_model=List[schemas_event.EventosPorStatus],
    summary="Eventos agrupados por status",
    description="""
    Retorna eventos agrupados por status com percentuais.
    
    Útil para gráficos de pizza mostrando distribuição de status.
    
    **Filtros opcionais:**
    - `data_inicio`: Filtrar eventos a partir desta data
    - `data_fim`: Filtrar eventos até esta data
    """,
)
def get_eventos_por_status(
    db: Session = Depends(deps.get_db),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Retorna eventos agrupados por status.
    """
    log_info("Buscando eventos por status", extra={"user_id": current_user.id})

    return crud_event.get_eventos_por_status(
        db=db,
        current_user=current_user,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get(
    "/stats/top-clientes",
    response_model=List[schemas_event.TopClientes],
    summary="Top clientes por valor",
    description="""
    Retorna os clientes com maior valor total em contratos.
    
    **Parâmetros:**
    - `limit`: Quantidade de clientes a retornar (padrão: 10)
    - `data_inicio`: Filtrar eventos a partir desta data
    - `data_fim`: Filtrar eventos até esta data
    
    **Exemplos:**
    - Top 5 clientes: `?limit=5`
    - Top 10 clientes do ano: `?limit=10&data_inicio=2025-01-01&data_fim=2025-12-31`
    """,
)
def get_top_clientes(
    db: Session = Depends(deps.get_db),
    limit: int = Query(
        10, ge=1, le=100, description="Quantidade de clientes a retornar"
    ),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Retorna os top clientes por valor de contratos.
    """
    log_info(
        "Buscando top clientes", extra={"user_id": current_user.id, "limit": limit}
    )

    return crud_event.get_top_clientes(
        db=db,
        current_user=current_user,
        limit=limit,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get(
    "/stats/despesas-por-insumo",
    response_model=List[schemas_event.DespesasPorInsumo],
    summary="Despesas agrupadas por insumo",
    description="""
    Retorna as despesas agrupadas por insumo com totais.
    
    Útil para análise de custos e identificação dos insumos mais caros.
    
    **Parâmetros:**
    - `limit`: Quantidade de insumos a retornar (padrão: 10)
    - `data_inicio`: Filtrar eventos a partir desta data
    - `data_fim`: Filtrar eventos até esta data
    
    **Exemplos:**
    - Top 5 insumos mais caros: `?limit=5`
    - Despesas do mês: `?data_inicio=2025-12-01&data_fim=2025-12-31`
    """,
)
def get_despesas_por_insumo(
    db: Session = Depends(deps.get_db),
    limit: int = Query(
        10, ge=1, le=100, description="Quantidade de insumos a retornar"
    ),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Retorna despesas agrupadas por insumo.
    """
    log_info(
        "Buscando despesas por insumo",
        extra={"user_id": current_user.id, "limit": limit},
    )

    return crud_event.get_despesas_por_insumo(
        db=db,
        current_user=current_user,
        limit=limit,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get(
    "/stats/dashboard",
    response_model=schemas_event.DashboardData,
    summary="Dados completos para dashboard",
    description="""
    Retorna todos os dados necessários para montar um dashboard completo.
    
    **Inclui:**
    - Estatísticas gerais
    - Eventos por mês
    - Eventos por status
    - Top 10 clientes
    - Top 10 insumos mais caros
    
    **Filtros opcionais:**
    - `data_inicio`: Filtrar eventos a partir desta data
    - `data_fim`: Filtrar eventos até esta data
    - `top_limit`: Quantidade de itens nos tops (padrão: 10)
    
    **Exemplo:**
    - Dashboard do ano: `?data_inicio=2025-01-01&data_fim=2025-12-31&top_limit=5`
    """,
)
def get_dashboard_data(
    db: Session = Depends(deps.get_db),
    data_inicio: Optional[date] = Query(
        None, description="Data inicial (formato: YYYY-MM-DD)"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final (formato: YYYY-MM-DD)"
    ),
    top_limit: int = Query(
        10, ge=1, le=50, description="Quantidade de itens nos rankings"
    ),
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """
    Retorna dados completos para dashboard em uma única requisição.
    """
    log_info(
        "Buscando dados completos do dashboard",
        extra={
            "user_id": current_user.id,
            "data_inicio": str(data_inicio) if data_inicio else None,
            "data_fim": str(data_fim) if data_fim else None,
        },
    )

    # Buscar todos os dados em paralelo
    estatisticas_gerais = crud_event.get_eventos_stats(
        db=db,
        current_user=current_user,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    eventos_por_mes = crud_event.get_eventos_por_mes(
        db=db,
        current_user=current_user,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    eventos_por_status = crud_event.get_eventos_por_status(
        db=db,
        current_user=current_user,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    top_clientes = crud_event.get_top_clientes(
        db=db,
        current_user=current_user,
        limit=top_limit,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    despesas_por_insumo = crud_event.get_despesas_por_insumo(
        db=db,
        current_user=current_user,
        limit=top_limit,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    log_info(
        "Dados do dashboard recuperados com sucesso",
        extra={
            "user_id": current_user.id,
            "total_eventos": estatisticas_gerais["total_eventos"],
            "meses_com_dados": len(eventos_por_mes),
        },
    )

    return {
        "estatisticas_gerais": estatisticas_gerais,
        "eventos_por_mes": eventos_por_mes,
        "eventos_por_status": eventos_por_status,
        "top_clientes": top_clientes,
        "despesas_por_insumo": despesas_por_insumo,
    }


# ========== ENDPOINTS DE DESPESAS ==========


@router.post(
    "/{evento_id}/despesas",
    response_model=schemas_event.Despesa,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar despesa ao evento",
    description="Adiciona uma nova despesa a um evento existente",
    responses={
        201: {"description": "Despesa criada com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para modificar este evento"},
        404: {"description": "Evento ou insumo não encontrado"},
    },
)
def add_despesa_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_in: schemas_event.DespesaCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Adiciona uma despesa a um evento."""
    log_info(
        "Adicionando despesa ao evento",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "insumo_id": despesa_in.id_insumo,
            "valor_total": float(despesa_in.vlr_total_pago),
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    despesa = crud_event.add_despesa_to_evento(
        db=db, evento_id=evento_id, despesa_in=despesa_in, user_id=current_user.id
    )

    log_info(
        "Despesa adicionada com sucesso",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "despesa_id": despesa.id,
            "insumo_id": despesa.id_insumo,
            "valor_total": float(despesa.vlr_total_pago),
        },
    )

    return despesa


@router.patch(
    "/{evento_id}/despesas/{despesa_id}",
    response_model=schemas_event.Despesa,
    summary="Atualizar despesa",
    description="Atualiza os dados de uma despesa existente",
    responses={
        200: {"description": "Despesa atualizada com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para modificar esta despesa"},
        404: {"description": "Evento ou despesa não encontrada"},
    },
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
    log_info(
        "Atualizando despesa",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "despesa_id": despesa_id,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    despesa_obj = next((d for d in evento.despesas if d.id == despesa_id), None)
    if not despesa_obj:
        log_warning(
            "Despesa não encontrada",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "despesa_id": despesa_id,
            },
        )
        raise HTTPException(
            status_code=404,
            detail=f"Despesa com id {despesa_id} não encontrada neste evento.",
        )

    if (
        current_user.perfil != "administrativo"
        and despesa_obj.id_usuario_criador != current_user.id
    ):
        log_warning(
            "Tentativa de modificar despesa de outro usuário",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "despesa_id": despesa_id,
                "despesa_owner": despesa_obj.id_usuario_criador,
            },
        )
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para modificar esta despesa. Apenas o criador ou administradores podem editá-la.",
        )

    despesa_updated = crud_event.update_despesa(
        db=db, despesa_obj=despesa_obj, despesa_in=despesa_in
    )

    log_info(
        "Despesa atualizada com sucesso",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "despesa_id": despesa_id,
        },
    )

    return despesa_updated


@router.delete(
    "/{evento_id}/despesas/{despesa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar despesa",
    description="Remove uma despesa de um evento",
    responses={
        204: {"description": "Despesa deletada com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para deletar esta despesa"},
        404: {"description": "Evento ou despesa não encontrada"},
    },
)
def delete_despesa_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    despesa_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Remove uma despesa de um evento."""
    log_warning(
        "Deletando despesa",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "despesa_id": despesa_id,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    despesa_obj = next((d for d in evento.despesas if d.id == despesa_id), None)
    if not despesa_obj:
        log_warning(
            "Despesa não encontrada",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "despesa_id": despesa_id,
            },
        )
        raise HTTPException(
            status_code=404,
            detail=f"Despesa com id {despesa_id} não encontrada neste evento.",
        )

    if (
        current_user.perfil != "administrativo"
        and despesa_obj.id_usuario_criador != current_user.id
    ):
        log_warning(
            "Tentativa de deletar despesa de outro usuário",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "despesa_id": despesa_id,
                "despesa_owner": despesa_obj.id_usuario_criador,
            },
        )
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para deletar esta despesa. Apenas o criador ou administradores podem excluí-la.",
        )

    log_info(
        "Despesa deletada",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "despesa_id": despesa_id,
            "insumo_id": despesa_obj.id_insumo,
            "valor_total": float(despesa_obj.vlr_total_pago),
        },
    )

    crud_event.delete_despesa(db=db, despesa_obj=despesa_obj)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ========== ENDPOINTS DE DEGUSTAÇÕES ==========


@router.post(
    "/{evento_id}/degustacoes",
    response_model=schemas_event.Degustacao,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar degustação ao evento",
    description="Adiciona uma nova degustação a um evento existente",
    responses={
        201: {"description": "Degustação criada com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para modificar este evento"},
        404: {"description": "Evento não encontrado"},
    },
)
def add_degustacao_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_in: schemas_event.DegustacaoCreate,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Adiciona uma degustação a um evento."""
    log_info(
        "Adicionando degustação ao evento",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "data_degustacao": str(degustacao_in.data_degustacao),
            "status": degustacao_in.status,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    degustacao = crud_event.add_degustacao_to_evento(
        db=db, evento_id=evento_id, degustacao_in=degustacao_in, user_id=current_user.id
    )

    log_info(
        "Degustação adicionada com sucesso",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "degustacao_id": degustacao.id,
            "data_degustacao": str(degustacao.data_degustacao),
            "status": degustacao.status,
        },
    )

    return degustacao


@router.patch(
    "/{evento_id}/degustacoes/{degustacao_id}",
    response_model=schemas_event.Degustacao,
    summary="Atualizar degustação",
    description="Atualiza os dados de uma degustação existente",
    responses={
        200: {"description": "Degustação atualizada com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para modificar esta degustação"},
        404: {"description": "Evento ou degustação não encontrada"},
    },
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
    log_info(
        "Atualizando degustação",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "degustacao_id": degustacao_id,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    degustacao_obj = next(
        (d for d in evento.degustacoes if d.id == degustacao_id), None
    )
    if not degustacao_obj:
        log_warning(
            "Degustação não encontrada",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "degustacao_id": degustacao_id,
            },
        )
        raise HTTPException(
            status_code=404,
            detail=f"Degustação com id {degustacao_id} não encontrada neste evento.",
        )

    if (
        current_user.perfil != "administrativo"
        and degustacao_obj.id_usuario_criador != current_user.id
    ):
        log_warning(
            "Tentativa de modificar degustação de outro usuário",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "degustacao_id": degustacao_id,
                "degustacao_owner": degustacao_obj.id_usuario_criador,
            },
        )
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para modificar esta degustação. Apenas o criador ou administradores podem editá-la.",
        )

    degustacao_updated = crud_event.update_degustacao(
        db=db, degustacao_obj=degustacao_obj, degustacao_in=degustacao_in
    )

    log_info(
        "Degustação atualizada com sucesso",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "degustacao_id": degustacao_id,
        },
    )

    return degustacao_updated


@router.delete(
    "/{evento_id}/degustacoes/{degustacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar degustação",
    description="Remove uma degustação de um evento",
    responses={
        204: {"description": "Degustação deletada com sucesso"},
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão para deletar esta degustação"},
        404: {"description": "Evento ou degustação não encontrada"},
    },
)
def delete_degustacao_for_evento(
    *,
    db: Session = Depends(deps.get_db),
    evento_id: int,
    degustacao_id: int,
    current_user: models_user.User = Depends(deps.get_current_active_operational_user),
):
    """Remove uma degustação de um evento."""
    log_warning(
        "Deletando degustação",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "degustacao_id": degustacao_id,
        },
    )

    evento = crud_event.get_evento(db=db, evento_id=evento_id)
    validate_event_permission(evento, current_user, "modificar")

    degustacao_obj = next(
        (d for d in evento.degustacoes if d.id == degustacao_id),
        None,
    )
    if not degustacao_obj:
        log_warning(
            "Degustação não encontrada",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "degustacao_id": degustacao_id,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Degustação com id {degustacao_id} não encontrada neste evento.",
        )

    if (
        current_user.perfil != "administrativo"
        and degustacao_obj.id_usuario_criador != current_user.id
    ):
        log_warning(
            "Tentativa de deletar degustação de outro usuário",
            extra={
                "user_id": current_user.id,
                "evento_id": evento_id,
                "degustacao_id": degustacao_id,
                "degustacao_owner": degustacao_obj.id_usuario_criador,
            },
        )
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para deletar esta degustação. Apenas o criador ou administradores podem excluí-la.",
        )

    log_info(
        "Degustação deletada",
        extra={
            "user_id": current_user.id,
            "evento_id": evento_id,
            "degustacao_id": degustacao_id,
            "data_degustacao": str(degustacao_obj.data_degustacao),
            "status": degustacao_obj.status,
        },
    )

    crud_event.delete_degustacao(db=db, degustacao_obj=degustacao_obj)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
