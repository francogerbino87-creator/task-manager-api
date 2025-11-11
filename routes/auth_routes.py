from fastapi import APIRouter, HTTPException, status, Depends
from schemas.user_schema import UserCreate, UserInDB, Token
from repositories.user_repository import UserRepository
from services.auth_service import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from config.settings import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Inyectamos la dependencia del repositorio
def get_user_repository():
    return UserRepository()

# --- Ruta de Registro de Usuario (POST /auth/register) ---
@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    user_repo: UserRepository = Depends(get_user_repository)
):
    # 1. Verificar si el email ya existe
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )

    # 2. Hashear la contraseña
    hashed_password = get_password_hash(user_data.password)

    # 3. Crear el usuario en la base de datos
    new_user = await user_repo.create(user_data, hashed_password)

    # 4. Devolver el usuario (excluyendo el hash)
    return new_user


# --- Ruta de Inicio de Sesión (POST /auth/login) ---
@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_data: UserCreate, # Usamos UserCreate para obtener email y password
    user_repo: UserRepository = Depends(get_user_repository)
):
    # 1. Buscar el usuario por email
    user_in_db = await user_repo.get_by_email(user_data.email)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar la contraseña
    if not verify_password(user_data.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Crear el Token de Acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user_in_db.id}, # Usamos 'sub' para el ID del usuario
        expires_delta=access_token_expires
    )
    
    # 4. Devolver el Token
    return {"access_token": access_token, "token_type": "bearer"}