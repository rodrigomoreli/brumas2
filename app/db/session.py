from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Cria o "motor" do SQLAlchemy.
# O 'pool_pre_ping=True' verifica se a conexão com o banco ainda está viva antes de usá-la.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Cria uma classe 'SessionLocal' que será usada para criar sessões de banco de dados.
# Cada instância de SessionLocal será uma sessão de banco de dados.
# autocommit=False e autoflush=False são as configurações padrão e mais seguras.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
