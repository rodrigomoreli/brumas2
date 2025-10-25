import asyncio
from app.db.session import SessionLocal
from app.crud import crud_user
from app.schemas.user import UserCreate, UserProfile

async def create_first_user():
    print("Iniciando a criação do superusuário...")
    db = SessionLocal()
    
    # --- DEFINA AQUI OS DADOS DO SEU SUPERUSUÁRIO ---
    SUPERUSER_EMAIL = "admin@brumas.com"
    SUPERUSER_USERNAME = "admin"
    SUPERUSER_PASSWORD = "admin_password_segura" # Troque por uma senha forte
    # -------------------------------------------------

    user = crud_user.get_user_by_email(db, email=SUPERUSER_EMAIL)
    if not user:
        user_in = UserCreate(
            email=SUPERUSER_EMAIL,
            username=SUPERUSER_USERNAME,
            password=SUPERUSER_PASSWORD,
            perfil=UserProfile.ADMINISTRATIVO,
            is_active=True
        )
        user = crud_user.create_user(db=db, user_in=user_in)
        print(f"Superusuário '{SUPERUSER_USERNAME}' criado com sucesso!")
    else:
        print(f"Superusuário com email '{SUPERUSER_EMAIL}' já existe.")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(create_first_user())
