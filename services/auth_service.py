from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import jwt, JWTError

from config.settings import settings # Importamos la configuración global

# Contexto para el hashing de contraseñas (usaremos bcrypt)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Hashing de Contraseñas ---

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña dada."""
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash."""
    return password_context.verify(plain_password, hashed_password)

# --- Funciones de JWT (JSON Web Token) ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Por defecto, el token expira en 60 minutos
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Codificamos el token usando la clave secreta y el algoritmo
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# Nota: La función para decodificar y obtener el usuario (dependencia de FastAPI) la haremos más tarde
# en un archivo de dependencias o directamente en las rutas.