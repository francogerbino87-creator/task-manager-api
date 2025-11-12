from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from config.settings import settings
from schemas.user_schema import UserCreate, UserInDB, Token
from services.auth_service import (
    verify_password, 
    create_access_token, 
    get_current_user_id # Importamos para usarlo como dependencia en futuras rutas
)
from repositories.user_repository import UserRepository

# Crea una instancia de APIRouter con el prefijo /auth y tags para Swagger
router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)

# Dependencia para obtener una instancia del repositorio de usuarios
def get_user_repository(repo: UserRepository = Depends(UserRepository)):
    """Inyecta la dependencia del repositorio de usuarios."""
    return repo

# --- 1. REGISTRO DE USUARIO ---
@router.post(
    "/register", 
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario"
)
async def register_user(
    user_data: UserCreate, 
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    """
    Registra un nuevo usuario en la base de datos, verificando que el email no exista.
    """
    # 1. Verificar si el usuario ya existe
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )

    # 2. Crear el nuevo usuario (la lógica de hasheo está en el repositorio)
    new_user = await user_repo.create_user(user_data)
    
    # 3. Retornar el esquema UserInDB sin la contraseña hasheada
    return new_user

# --- 2. INICIO DE SESIÓN (OBTENER TOKEN) ---
@router.post(
    "/token", 
    response_model=Token,
    summary="Obtener un token JWT para iniciar sesión"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    """
    Verifica las credenciales de email/contraseña y devuelve un token JWT.
    """
    # 1. Buscar usuario por email (username en OAuth2PasswordRequestForm es el email)
    user = await user_repo.get_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Credenciales inválidas
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. Crear el token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.id}, # El 'sub' (subject) es el ID del usuario
        expires_delta=access_token_expires
    )
    
    # 3. Retornar el token
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. RUTA DE PRUEBA (Para verificar el token) ---
# Esta ruta utiliza la dependencia get_current_user_id
@router.get(
    "/me", 
    response_model=UserInDB,
    summary="Obtener la información del usuario actual autenticado"
)
async def read_users_me(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    """
    Requiere un token JWT válido. Devuelve los datos del usuario asociado al token.
    """
    user = await user_repo.get_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
        
    return user