from typing import TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError #
from config.settings import settings
from services.auth_service import get_current_user as auth_get_current_user 

# Define el esquema de seguridad OAuth2 (necesario para la documentación de Swagger)
# Apunta al endpoint de login que definimos: /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

if TYPE_CHECKING:
    from schemas.user_schema import TokenData, UserInDB
    from repositories.user_repository import UserRepository
    from repositories.task_repository import TaskRepository

# 1. Dependencia del Repositorio de Usuarios
# Inyectamos el repositorio (igual que en las rutas)
def get_user_repository() -> UserRepository:
    from db.mongodb import mongodb
    from repositories.user_repository import UserRepository
    """Retorna una instancia del repositorio de usuarios."""
    if mongodb is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected.")
    # El UserRepository usa 'mongodb' por defecto en su constructor (si lo definimos así)
    return UserRepository(mongodb)

# 2. Dependencia del Repositorio de Tareas
def get_task_repository() -> TaskRepository:
    from repositories.task_repository import TaskRepository
    from db.mongodb import mongodb
    """Retorna una instancia del repositorio de tareas."""
    if mongodb is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected.")
    return TaskRepository(mongodb)

# 3. Dependencia de Autenticación
# Exponemos la función de autenticación del servicio para usarla en los routers
def get_authenticated_user(user_in_db = Depends(auth_get_current_user)):
    """Dependencia que retorna el objeto UserInDB ya validado."""
    return user_in_db

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    user_repo: UserRepository = Depends(get_user_repository)
) -> 'UserInDB':
    """
    Decodifica el token JWT y devuelve el objeto UserInDB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decodificar el token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # 2. Extraer el subject (sub) que es nuestro user_id
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # 3. Buscar el usuario en la base de datos
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    return user