from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

# FIX CRÍTICO: Importar get_db desde config.database (que es async)
from config.database import get_db as get_database 
from repositories.user_repository import UserRepository
from repositories.task_repository import TaskRepository
from schemas.user_schema import UserInDB
from app.core.security import decode_access_token, ALGORITHM # Necesitamos ALGORITHM para la verificación de token

# Esquema de seguridad OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# --- 1. Dependencia para la base de datos (DI) ---
# get_database ya es una dependencia async de FastAPI, así que la usamos directamente

# --- 2. Dependencia para el Repositorio de Usuarios ---
def get_user_repository(db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]):
    """Dependencia que retorna una instancia del repositorio de usuarios."""
    return UserRepository(db)

# --- 3. Dependencia para el Repositorio de Tareas ---
def get_task_repository(db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]):
    """Dependencia que retorna una instancia del repositorio de tareas."""
    return TaskRepository(db)

# --- 4. Dependencia para el Usuario Autenticado (Protección de Rutas) ---
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserInDB:
    """
    Decodifica el token JWT y busca el usuario asociado en la base de datos.
    Lanza 401 Unauthorized si el token es inválido, expira o el usuario no existe.
    """
    
    # 1. Verificar y decodificar el token (maneja expiración y firma inválida)
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: ID de usuario faltante",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Buscar el usuario en la base de datos
    user = await user_repo.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario asociado al token no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Retornar el usuario autenticado
    return user
        
    # 3. Retornar el objeto Pydantic UserInDB
    return user