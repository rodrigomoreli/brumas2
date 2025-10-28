# app/crud/crud_user.py

"""
Operações CRUD para usuários.

Define funções para criação, leitura, atualização e exclusão de usuários
utilizando SQLAlchemy e os schemas definidos na aplicação.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
import app.models.user as models_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Busca um usuário pelo ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Busca um usuário pelo e-mail."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Busca um usuário pelo nome de usuário."""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Retorna uma lista paginada de usuários."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, *, user_in: UserCreate) -> User:
    """Cria um novo usuário com senha criptografada."""
    user_data = user_in.model_dump(exclude={"password"})
    hashed_password = get_password_hash(user_in.password)
    db_user = User(**user_data, hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, *, db_user: User, user_in: UserUpdate) -> User:
    """Atualiza os dados de um usuário existente."""
    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"] is not None:
        hashed_password = get_password_hash(update_data.pop("password"))
        update_data["hashed_password"] = hashed_password
    else:
        update_data.pop("password", None)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, *, user_to_delete: models_user.User) -> None:
    """Remove um usuário do banco de dados."""
    db.delete(user_to_delete)
    db.commit()
