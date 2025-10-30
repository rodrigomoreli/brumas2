"""
Testes para endpoints de dimensões.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_create_cliente(client: TestClient, operational_token: str):
    """Testa criação de cliente."""
    response = client.post(
        "/api/v1/dimensions/clientes/",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "nome": "Cliente Novo",
            "email": "cliente_novo@test.com",
            "contato_principal": "João Silva",
            "telefone": "11999999999",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Cliente Novo"
    assert data["email"] == "cliente_novo@test.com"


@pytest.mark.integration
def test_list_clientes(client: TestClient, operational_token: str, sample_cliente):
    """Testa listagem de clientes."""
    response = client.get(
        "/api/v1/dimensions/clientes/",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(c["nome"] == "Cliente Teste" for c in data)


@pytest.mark.integration
def test_get_cliente_by_id_as_creator(
    client: TestClient, operational_token: str, db, operational_user
):
    """
    Testa busca de cliente por ID quando o usuário é o criador.
    ✅ CORRIGIDO: Criar cliente com o usuário operacional
    """
    from app.models.dimension import Cliente

    # Criar cliente com o usuário operacional
    cliente = Cliente(
        nome="Cliente do Operacional",
        email="operacional_cliente@test.com",
        id_usuario_criador=operational_user.id,  # ✅ Criado pelo usuário operacional
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    response = client.get(
        f"/api/v1/dimensions/clientes/{cliente.id}",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cliente.id
    assert data["nome"] == "Cliente do Operacional"


@pytest.mark.integration
def test_get_cliente_by_id_as_admin(
    client: TestClient, admin_token: str, sample_cliente
):
    """
    Testa que admin pode ver qualquer cliente.
    ✅ NOVO TESTE
    """
    response = client.get(
        f"/api/v1/dimensions/clientes/{sample_cliente.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_cliente.id
    assert data["nome"] == "Cliente Teste"


@pytest.mark.integration
def test_get_cliente_by_id_permission_denied(
    client: TestClient, operational_token: str, sample_cliente
):
    """
    Testa que usuário operacional NÃO pode ver cliente de outro usuário.
    ✅ NOVO TESTE
    """
    # sample_cliente foi criado pelo admin_user
    response = client.get(
        f"/api/v1/dimensions/clientes/{sample_cliente.id}",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


@pytest.mark.integration
def test_delete_cliente_as_operational_forbidden(
    client: TestClient, operational_token: str, sample_cliente
):
    """
    Testa que usuário operacional NÃO pode deletar clientes.
    """
    response = client.delete(
        f"/api/v1/dimensions/clientes/{sample_cliente.id}",
        headers={"Authorization": f"Bearer {operational_token}"},
    )

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


@pytest.mark.integration
def test_delete_cliente_as_admin_success(
    client: TestClient, admin_token: str, db, admin_user
):
    """
    Testa que usuário ADMIN pode deletar clientes.
    """
    from app.models.dimension import Cliente

    # Criar um cliente para deletar
    cliente = Cliente(
        nome="Cliente Para Deletar",
        email="deletar@test.com",
        id_usuario_criador=admin_user.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    response = client.delete(
        f"/api/v1/dimensions/clientes/{cliente.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code in [200, 204]
