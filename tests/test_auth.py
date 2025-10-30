# tests/test_auth.py

"""
Testes para autenticação e autorização.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_login_success(client: TestClient, admin_user):
    """Testa login com credenciais válidas."""
    response = client.post(
        "/login/access-token", data={"username": "admin_test", "password": "admin123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.unit
def test_login_invalid_username(client: TestClient):
    """Testa login com username inválido."""
    response = client.post(
        "/login/access-token",
        data={"username": "invalid_user", "password": "password123"},
    )

    assert response.status_code == 401
    assert "Username ou senha incorretos" in response.json()["detail"]


@pytest.mark.unit
def test_login_invalid_password(client: TestClient, admin_user):
    """Testa login com senha inválida."""
    response = client.post(
        "/login/access-token",
        data={"username": "admin_test", "password": "wrong_password"},
    )

    assert response.status_code == 401
    assert "Username ou senha incorretos" in response.json()["detail"]


@pytest.mark.unit
def test_access_protected_endpoint_without_token(client: TestClient):
    """Testa acesso a endpoint protegido sem token."""
    response = client.get("/api/v1/eventos/")

    assert response.status_code == 401


@pytest.mark.unit
def test_access_protected_endpoint_with_invalid_token(client: TestClient):
    """Testa acesso a endpoint protegido com token inválido."""
    response = client.get(
        "/api/v1/eventos/", headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 403
