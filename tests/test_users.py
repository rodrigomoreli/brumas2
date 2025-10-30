"""
Testes para endpoints de usuários.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_create_user_as_admin(client: TestClient, admin_token: str):
    """Testa criação de usuário por admin."""
    response = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "novo_usuario",
            "email": "novo@test.com",
            "password": "senha123",
            "nome_completo": "Novo Usuário",
            "perfil": "operacional",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "novo_usuario"
    assert data["email"] == "novo@test.com"
    assert data["perfil"] == "operacional"
    assert "hashed_password" not in data


@pytest.mark.integration
def test_create_user_as_operational_forbidden(
    client: TestClient, operational_token: str
):
    """Testa que usuário operacional não pode criar usuários."""
    response = client.post(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {operational_token}"},
        json={
            "username": "novo_usuario",
            "email": "novo@test.com",
            "password": "senha123",
            "nome_completo": "Novo Usuário",
            "perfil": "operacional",
        },
    )

    assert response.status_code == 403


@pytest.mark.integration
def test_list_users_as_admin(
    client: TestClient, admin_token: str, admin_user, operational_user
):
    """Testa listagem de usuários por admin."""
    response = client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(u["username"] == "admin_test" for u in data)
    assert any(u["username"] == "operacional_test" for u in data)


@pytest.mark.integration
def test_get_user_by_id(client: TestClient, admin_token: str, operational_user):
    """Testa busca de usuário por ID."""
    response = client.get(
        f"/api/v1/users/{operational_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == operational_user.id
    assert data["username"] == "operacional_test"


@pytest.mark.integration
def test_update_user(client: TestClient, admin_token: str, operational_user):
    """Testa atualização de usuário."""
    response = client.put(
        f"/api/v1/users/{operational_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nome_completo": "Operacional Atualizado",
            "is_active": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nome_completo"] == "Operacional Atualizado"


@pytest.mark.integration
def test_delete_user(client: TestClient, admin_token: str, operational_user):
    """Testa deleção de usuário."""
    response = client.delete(
        f"/api/v1/users/{operational_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204

    # Verificar que usuário foi deletado
    response = client.get(
        f"/api/v1/users/{operational_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_admin_cannot_delete_self(client: TestClient, admin_token: str, admin_user):
    """Testa que admin não pode se auto-deletar."""
    response = client.delete(
        f"/api/v1/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 403
    assert "não podem deletar a si mesmos" in response.json()["detail"]
