"""
Configurações e fixtures compartilhadas para os testes.
"""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.api import deps
from app.core import security
from app.models.user import User, UserProfile
from app.models.dimension import (
    Cliente,
    LocalEvento,
    Cidade,
    Buffet,
    Assessoria,
    TipoEvento,
    Insumo,
    UnidadeMedida,
)
from app.models.event import Evento, Despesa, Degustacao, EventoStatus, DegustacaoStatus

# Banco de dados em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# ✅ ADICIONAR: Habilitar foreign keys no SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Fixture que cria um banco de dados limpo para cada teste.
    """
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Dropar todas as tabelas após o teste
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Fixture que cria um cliente de teste com banco de dados mockado.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[deps.get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db) -> User:
    """
    Fixture que cria um usuário administrador para testes.
    """
    user = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=security.get_password_hash("admin123"),
        nome_completo="Admin Test",
        perfil=UserProfile.ADMINISTRATIVO,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def operational_user(db) -> User:
    """
    Fixture que cria um usuário operacional para testes.
    """
    user = User(
        username="operacional_test",
        email="operacional@test.com",
        hashed_password=security.get_password_hash("oper123"),
        nome_completo="Operacional Test",
        perfil=UserProfile.OPERACIONAL,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user) -> str:
    """
    Fixture que retorna um token JWT válido para usuário admin.
    """
    response = client.post(
        "/login/access-token", data={"username": "admin_test", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def operational_token(client, operational_user) -> str:
    """
    Fixture que retorna um token JWT válido para usuário operacional.
    """
    response = client.post(
        "/login/access-token",
        data={"username": "operacional_test", "password": "oper123"},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def sample_cliente(db, admin_user) -> Cliente:
    """
    Fixture que cria um cliente de exemplo para testes.
    """
    cliente = Cliente(
        nome="Cliente Teste",
        email="cliente@test.com",
        contato_principal="João Silva",
        telefone="11999999999",
        id_usuario_criador=admin_user.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@pytest.fixture(scope="function")
def sample_local_evento(db, admin_user) -> LocalEvento:
    """
    Fixture que cria um local de evento de exemplo para testes.
    """
    local = LocalEvento(
        descricao="Salão de Festas Teste",
        endereco="Rua Teste, 123",
        capacidade_maxima=200,
        id_usuario_criador=admin_user.id,
    )
    db.add(local)
    db.commit()
    db.refresh(local)
    return local


@pytest.fixture(scope="function")
def sample_cidade(db, admin_user) -> Cidade:
    """
    Fixture que cria uma cidade de exemplo para testes.
    """
    cidade = Cidade(
        nome="São Paulo",
        estado="SP",
        id_usuario_criador=admin_user.id,
    )
    db.add(cidade)
    db.commit()
    db.refresh(cidade)
    return cidade


@pytest.fixture(scope="function")
def sample_buffet(db, admin_user) -> Buffet:
    """
    Fixture que cria um buffet de exemplo para testes.
    """
    buffet = Buffet(
        descricao="Buffet Gourmet Teste",
        contato="Maria Santos",
        telefone="11988888888",
        id_usuario_criador=admin_user.id,
    )
    db.add(buffet)
    db.commit()
    db.refresh(buffet)
    return buffet


@pytest.fixture(scope="function")
def sample_insumo(db, admin_user) -> Insumo:
    """
    Fixture que cria um insumo de exemplo para testes.
    """
    insumo = Insumo(
        descricao="Carne Bovina",
        tipo_insumo="Proteína",
        unidade_medida=UnidadeMedida.KG,
        vlr_referencia=50.00,
        id_usuario_criador=admin_user.id,
    )
    db.add(insumo)
    db.commit()
    db.refresh(insumo)
    return insumo


@pytest.fixture(scope="function")
def sample_evento(db, operational_user, sample_cliente, sample_local_evento) -> Evento:
    """
    Fixture que cria um evento de exemplo para testes.
    ✅ CORRIGIDO: Usar operational_user ao invés de admin_user
    """
    from datetime import date

    evento = Evento(
        data_evento=date(2025, 12, 15),
        horas_festa=6.0,
        qtde_convidados_prevista=150,
        status_evento=EventoStatus.ORCAMENTO,
        id_cliente=sample_cliente.id,
        id_local_evento=sample_local_evento.id,
        id_usuario_criador=operational_user.id,  # ✅ CORRIGIDO
        vlr_unitario_por_convidado=120.00,
        vlr_total_contrato=18000.00,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento
