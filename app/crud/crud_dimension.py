# app/crud/crud_dimension.py
from app.crud.base import CRUDBase
from app.models import dimension as models

from app.schemas import dimension as schemas_dim
from app.schemas import event as schemas_event

# Para cada dimensão, criado uma classe que herda da base
class CRUDAssessoria(CRUDBase[models.Assessoria, schemas_dim.AssessoriaCreate, schemas_dim.AssessoriaUpdate]):
    pass
crud_assessoria = CRUDAssessoria(models.Assessoria)

class CRUDBuffet(CRUDBase[models.Buffet, schemas_dim.BuffetCreate, schemas_dim.BuffetUpdate]):
    pass
crud_buffet = CRUDBuffet(models.Buffet)

class CRUDCidade(CRUDBase[models.Cidade, schemas_dim.CidadeCreate, schemas_dim.CidadeUpdate]):
    pass
crud_cidade = CRUDCidade(models.Cidade)

class CRUDCliente(CRUDBase[models.Cliente, schemas_dim.ClienteCreate, schemas_dim.ClienteUpdate]):
    pass
crud_cliente = CRUDCliente(models.Cliente)

class CRUDInsumo(CRUDBase[models.Insumo, schemas_dim.InsumoCreate, schemas_dim.InsumoUpdate]):
    pass
crud_insumo = CRUDInsumo(models.Insumo)

class CRUDLocalEvento(CRUDBase[models.LocalEvento, schemas_dim.LocalEventoCreate, schemas_dim.LocalEventoUpdate]):
    pass
crud_local_evento = CRUDLocalEvento(models.LocalEvento)

class CRUDTipoEvento(CRUDBase[models.TipoEvento, schemas_dim.TipoEventoCreate, schemas_dim.TipoEventoUpdate]):
    pass
crud_tipo_evento = CRUDTipoEvento(models.TipoEvento)

# Instanciamos um objeto para cada classe para ser usado nos endpoints
assessoria = CRUDAssessoria(models.Assessoria)
buffet = CRUDBuffet(models.Buffet)
cidade = CRUDCidade(models.Cidade)
cliente = CRUDCliente(models.Cliente)
insumo = CRUDInsumo(models.Insumo)
local_evento = CRUDLocalEvento(models.LocalEvento)
tipo_evento = CRUDTipoEvento(models.TipoEvento)
