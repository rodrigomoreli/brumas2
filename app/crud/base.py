from typing import Any, Generic, List, Optional, Type, TypeVar, Union, Dict
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.base import Base


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType, user_id: Optional[int] = None) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        if user_id is not None:
            if hasattr(db_obj, "id_usuario_criador"):
                setattr(db_obj, "id_usuario_criador", user_id)
            elif hasattr(db_obj, "usuario_criador_id"):
                setattr(db_obj, "usuario_criador_id", user_id)
            elif hasattr(db_obj, "created_by"):
                setattr(db_obj, "created_by", user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Atualiza um objeto no banco de dados.

        :param db: A sessão do banco de dados.
        :param db_obj: O objeto SQLAlchemy a ser atualizado.
        :param obj_in: Os dados de atualização (um schema Pydantic ou um dicionário).
        :return: O objeto atualizado.
        """
        # Se os dados de entrada forem um schema, converta para um dicionário
        # usando exclude_unset=True para permitir atualizações parciais.
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        # Itera sobre os dados de atualização e os aplica ao objeto do banco
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Salva as mudanças no banco
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    