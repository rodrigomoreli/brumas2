# app/crud/crud_dimension.py

"""
Operações CRUD para entidades dimensionais.

Define classes específicas para cada modelo dimensional, herdando da
base genérica CRUDBase. Cada instância pode ser utilizada diretamente
nos endpoints da aplicação.
"""

from app.crud.base import CRUDBase
from app.models import dimension as models
from app.schemas import dimension as schemas_dim


class CRUDAssessoria(
    CRUDBase[
        models.Assessoria,
        schemas_dim.AssessoriaCreate,
        schemas_dim.AssessoriaUpdate,
    ]
):
    pass


class CRUDBuffet(
    CRUDBase[
        models.Buffet,
        schemas_dim.BuffetCreate,
        schemas_dim.BuffetUpdate,
    ]
):
    pass


class CRUDCidade(
    CRUDBase[
        models.Cidade,
        schemas_dim.CidadeCreate,
        schemas_dim.CidadeUpdate,
    ]
):
    pass


class CRUDCliente(
    CRUDBase[
        models.Cliente,
        schemas_dim.ClienteCreate,
        schemas_dim.ClienteUpdate,
    ]
):
    pass


class CRUDInsumo(
    CRUDBase[
        models.Insumo,
        schemas_dim.InsumoCreate,
        schemas_dim.InsumoUpdate,
    ]
):
    pass


class CRUDLocalEvento(
    CRUDBase[
        models.LocalEvento,
        schemas_dim.LocalEventoCreate,
        schemas_dim.LocalEventoUpdate,
    ]
):
    pass


class CRUDTipoEvento(
    CRUDBase[
        models.TipoEvento,
        schemas_dim.TipoEventoCreate,
        schemas_dim.TipoEventoUpdate,
    ]
):
    pass


# Instâncias para uso direto nos endpoints
crud_assessoria = CRUDAssessoria(models.Assessoria)
crud_buffet = CRUDBuffet(models.Buffet)
crud_cidade = CRUDCidade(models.Cidade)
crud_cliente = CRUDCliente(models.Cliente)
crud_insumo = CRUDInsumo(models.Insumo)
crud_local_evento = CRUDLocalEvento(models.LocalEvento)
crud_tipo_evento = CRUDTipoEvento(models.TipoEvento)
