from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config.settings import settings
from schemas.user_schema import TokenData, UserInDB
from repositories.user_repository import UserRepository

# Define el esquema de seguridad OAuth2 (necesario para la documentación de Swagger)
# Apunta al endpoint de login que definimos: /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Inyectamos el repositorio (igual que en las rutas)
def get_user_repository():
    return UserRepository()

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserInDB:
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
        
        token_data = TokenData(user_id=user_id)
        
    except JWTError:
        raise credentials_exception

    # 3. Buscar el usuario en la base de datos
    user = await user_repo.get_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
        
    return user