from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any
from bson import ObjectId

# Asegúrate de que las rutas de importación sean correctas:
from schemas.user_schema import UserCreate, Token, UserInDB
from db.mongodb import get_db # CORREGIDO: Importar desde 'db.mongodb'
from config.settings import settings # RUTA CORREGIDA: config.settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.dependencies import get_current_user # Se usará para rutas futuras
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
USERS_COLLECTION = settings.COLLECTION_USERS # Usamos el nombre de colección de settings


# --- RUTAS DE AUTENTICACIÓN ---

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate) -> Any:
    """Registra un nuevo usuario en la base de datos."""
    db = get_db()

    # 1. Verificar si el email ya existe
    existing_user = await db[USERS_COLLECTION].find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    # 2. Hashear la contraseña
    hashed_password = get_password_hash(user_in.password)

    # 3. Preparar el documento para MongoDB
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    # 4. Insertar en la DB
    result = await db[USERS_COLLECTION].insert_one(user_data)
    
    # 5. Obtener el usuario insertado (para el response_model)
    new_user = await db[USERS_COLLECTION].find_one({"_id": result.inserted_id})
    
    # 6. Mapear y devolver (UserInDB)
    if new_user:
        new_user['id'] = str(new_user.pop('_id'))
        return UserInDB(**new_user)
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo al recuperar el usuario registrado.")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Inicia sesión y devuelve un token JWT.
    OAuth2PasswordRequestForm espera 'username' (usaremos 'email') y 'password'.
    """
    db = get_db()
    
    # 1. Buscar el usuario por email (username)
    user_dict = await db[USERS_COLLECTION].find_one({"email": form_data.username})
    
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas (Email)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verificar la contraseña
    if not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas (Contraseña)",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Crear el token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # El 'sub' (subject) del token será el ID del usuario
    access_token = create_access_token(
        data={"sub": str(user_dict["_id"])},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- RUTA DE PRUEBA (Utiliza get_current_user) ---
@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Requiere un token JWT válido. Devuelve los datos del usuario asociado al token."""
    # current_user es el documento de MongoDB, solo mapeamos a Pydantic
    current_user['id'] = str(current_user.pop('_id'))
    return UserInDB(**current_user)