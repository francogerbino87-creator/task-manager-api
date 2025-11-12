from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from config.settings import settings
from schemas.user_schema import TokenData

# --- Configuración de Seguridad ---

# Esquema para el manejo de contraseñas (usamos bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad para FastAPI (para obtener el token del header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Funciones de Hashing de Contraseña ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña plana."""
    return pwd_context.hash(password)

# --- Funciones de Token JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT con datos y tiempo de expiración."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Si no se especifica expiración, usa la configuración por defecto
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # El 'sub' (subject) es el estándar para identificar al usuario (ej. su ID)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """Decodifica el token de acceso JWT y verifica su validez."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token usando la clave secreta y el algoritmo
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # El sub (subject) debe ser la clave primaria (ID del usuario)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        # Retorna los datos del token con el ID del usuario
        token_data = TokenData(sub=user_id)
        return token_data
        
    except JWTError:
        # Error genérico de JWT (expiración, firma inválida, etc.)
        raise credentials_exception

# --- Dependencia de Autenticación de FastAPI ---
# Esta función se usará en los endpoints que requieren un usuario logueado.

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependencia de FastAPI para obtener el ID del usuario autenticado
    a partir del token JWT.
    """
    # Usamos decode_access_token para obtener el ID
    token_data = decode_access_token(token)
    
    # Si token_data.sub es None, decode_access_token ya habría lanzado una excepción,
    # pero verificamos de nuevo por seguridad
    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data.sub