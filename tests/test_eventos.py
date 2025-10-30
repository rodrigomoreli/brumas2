"""
Testes para endpoints de eventos.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date


@pytest.mark.integration
def test_create_evento_success(
    client: TestClient, operational_token: str, sample_cliente, sample_local_evento
):
    """Testa criação de evento com sucesso."""
    response = client.post(
        "/api/v1/eventos/",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "id_cliente": sample_cliente.id,
            "id_local_evento": sample_local_evento.id,
            "data_evento": "2025-12-20",
            "status_evento": "Orçamento",
            "qtde_convidados_prevista": 100,
            "vlr_unitario_por_convidado": 150.00,
            "vlr_total_contrato": 15000.00,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id_cliente"] == sample_cliente.id
    assert data["id_local_evento"] == sample_local_evento.id
    assert data["status_evento"] == "Orçamento"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.integration
def test_create_evento_invalid_cliente(
    client: TestClient, operational_token: str, sample_local_evento
):
    """Testa criação de evento com cliente inexistente."""
    response = client.post(
        "/api/v1/eventos/",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "id_cliente": 99999,  # ID inexistente
            "id_local_evento": sample_local_evento.id,
            "data_evento": "2025-12-20",
            "status_evento": "Orçamento",
        },
    )

    assert response.status_code == 404
    assert "Cliente" in response.json()["detail"]


@pytest.mark.integration
def test_get_evento_by_id(client: TestClient, operational_token: str, sample_evento):
    """Testa busca de evento por ID."""
    response = client.get(
        f"/api/v1/eventos/{sample_evento.id}/",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_evento.id
    assert data["id_cliente"] == sample_evento.id_cliente
    assert "cliente_nome" in data
    assert "local_evento_nome" in data


@pytest.mark.integration
def test_get_evento_not_found(client: TestClient, operational_token: str):
    """Testa busca de evento inexistente."""
    response = client.get(
        "/api/v1/eventos/99999/",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


@pytest.mark.integration
def test_list_eventos_with_pagination(
    client: TestClient, operational_token: str, sample_evento
):
    """Testa listagem de eventos com paginação."""
    response = client.get(
        "/api/v1/eventos/?page=1&page_size=10",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert "has_next" in data
    assert "has_previous" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) >= 1


@pytest.mark.integration
def test_list_eventos_with_filters(
    client: TestClient, operational_token: str, sample_evento
):
    """Testa listagem de eventos com filtros."""
    response = client.get(
        f"/api/v1/eventos/?status_evento=Orçamento&id_cliente={sample_evento.id_cliente}",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["status_evento"] == "Orçamento"
        assert item["id_cliente"] == sample_evento.id_cliente


@pytest.mark.integration
def test_update_evento_success(
    client: TestClient, operational_token: str, sample_evento
):
    """Testa atualização de evento com sucesso."""
    response = client.patch(
        f"/api/v1/eventos/{sample_evento.id}",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "status_evento": "Confirmado",
            "qtde_convidados_prevista": 180,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status_evento"] == "Confirmado"
    assert data["qtde_convidados_prevista"] == 180


@pytest.mark.integration
def test_update_evento_permission_denied(
    client: TestClient,
    operational_token: str,
    db,
    sample_cliente,
    sample_local_evento,
    admin_user,
):
    """Testa que usuário não pode atualizar evento de outro usuário."""
    from app.models.event import Evento, EventoStatus

    # Criar evento de outro usuário
    evento_outro_usuario = Evento(
        data_evento=date(2025, 12, 25),
        status_evento=EventoStatus.ORCAMENTO,
        id_cliente=sample_cliente.id,
        id_local_evento=sample_local_evento.id,
        id_usuario_criador=admin_user.id,  # Criado pelo admin
    )
    db.add(evento_outro_usuario)
    db.commit()
    db.refresh(evento_outro_usuario)

    # Tentar atualizar com token de usuário operacional
    response = client.patch(
        f"/api/v1/eventos/{evento_outro_usuario.id}",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={"status_evento": "Confirmado"},
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"]


@pytest.mark.integration
def test_delete_evento_success(
    client: TestClient, operational_token: str, sample_evento
):
    """Testa deleção de evento com sucesso."""
    response = client.delete(
        f"/api/v1/eventos/{sample_evento.id}",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 204

    # Verificar que evento foi deletado
    response = client.get(
        f"/api/v1/eventos/{sample_evento.id}/",
        headers={"Authorization": f"Bearer {operational_token}"},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_add_despesa_to_evento(
    client: TestClient, operational_token: str, sample_evento, sample_insumo
):
    """Testa adição de despesa a um evento."""
    response = client.post(
        f"/api/v1/eventos/{sample_evento.id}/despesas",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "id_insumo": sample_insumo.id,
            "quantidade": 50.0,
            "vlr_unitario_pago": 15.00,
            "vlr_total_pago": 750.00,
            "data_despesa": "2025-11-10",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id_insumo"] == sample_insumo.id
    assert float(data["quantidade"]) == 50.0
    assert float(data["vlr_total_pago"]) == 750.00


@pytest.mark.integration
def test_add_degustacao_to_evento(
    client: TestClient, operational_token: str, sample_evento
):
    """Testa adição de degustação a um evento."""
    response = client.post(
        f"/api/v1/eventos/{sample_evento.id}/degustacoes",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "data_degustacao": "2025-11-01",
            "status": "Agendada",
            "vlr_degustacao": 500.00,
            "feedback_cliente": None,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["data_degustacao"] == "2025-11-01"
    assert data["status"] == "Agendada"
    assert float(data["vlr_degustacao"]) == 500.00
