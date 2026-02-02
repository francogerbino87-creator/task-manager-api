from fastapi import Depends, HTTPException, status
# Usamos OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer 
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

# Importamos la función de decodificación y el esquema de usuario
from app.core.security import decode_access_token
from schemas.user_schema import UserInDB
from repositories.user_repository import UserRepository
# Usar ruta absoluta desde config.database
from config.database import get_db 

# Crea la instancia del esquema de seguridad (Bearer Token)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token", # Especifica el endpoint de token para que Swagger lo sepa
    scheme_name="JWTBearer", 
    description="Requiere un Token JWT en el encabezado 'Authorization: Bearer <token>'"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncIOMotorDatabase = Depends(get_db) 
) -> UserInDB:
    """
    Función de dependencia para obtener el usuario autenticado a partir del token JWT.
    """
    
    # 1. Decodificar el token para obtener el ID de usuario (subject)
    payload = decode_access_token(token)
    
    user_id: Optional[str] = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un ID de usuario válido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. Buscar el usuario en la base de datos por ID
    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o token revocado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Validar si el usuario está activo (opcional)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo.",
        )
        
    # 4. Devolver el objeto del usuario
    return user