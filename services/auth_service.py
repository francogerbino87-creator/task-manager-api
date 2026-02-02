from typing import Optional
from fastapi import HTTPException, status 

from schemas.user_schema import UserInDB, UserCreate
from repositories.user_repository import UserRepository
from app.core.security import create_access_token, get_password_hash, verify_password 

# --- Servicio de Autenticación (AuthService) ---

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_in: UserCreate) -> UserInDB:
        """
        Registra un nuevo usuario, hasheando la contraseña y verificando duplicidad.
        """
        # 1. Verificar si el email ya existe
        existing_user = await self.user_repository.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo electrónico ya está registrado.")
            
        try:
            # 2. HASHEAR LA CONTRASEÑA EN EL SERVICIO
            hashed_password = get_password_hash(user_in.password)
            
            # 3. Delegar la creación al repositorio, pasándole el hash.
            new_user = await self.user_repository.create_user(user_in, hashed_password)
            return new_user
            
        except ValueError as e:
            # Captura el error de 'Email already registered' que viene del repositorio
            print(f"DEBUG_ERROR: Valor inválido durante el registro: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            
        except Exception as e:
            # CAPTURA CUALQUIER OTRO ERROR (e.g., fallos de DB, PyMongoError)
            print(f"FATAL_ERROR: Falla de inserción en la base de datos: {e}")
            # Devolvemos un 500 para indicar que el fallo es del lado del servidor/DB
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error inesperado al crear el usuario. Por favor, revisa la consola del servidor."
            )


    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Autentica un usuario por email y contraseña."""
        
        user = await self.user_repository.get_by_email(email)
        
        if user and self.user_repository.verify_password(password, user.hashed_password):
            return user
        return None

    def create_user_token(self, user: UserInDB) -> str:
        """Crea el token JWT para un usuario autenticado."""
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
        )
        return access_token