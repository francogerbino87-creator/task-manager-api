from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Importación CRÍTICA para el login

# CRÍTICO: Importar get_db desde la nueva ubicación 'config/database'
from config.database import get_db 
from schemas.user_schema import UserCreate, Token
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from motor.motor_asyncio import AsyncIOMotorDatabase # Usamos IOMotorDatabase para el tipo

# --- Configuración de Router y Servicios ---

router = APIRouter(prefix="/auth", tags=["auth"])

# La dependencia ahora usa AsyncIOMotorDatabase
async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthService:
    """Inyector de dependencia para el AuthService."""
    # UserRepository espera AsyncIOMotorDatabase (ya corregido internamente en tu repositorio)
    user_repository = UserRepository(db)
    return AuthService(user_repository)

# --- 1. Endpoint de Registro ---
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register_user(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """
    Registra un nuevo usuario y devuelve un token de acceso inmediatamente.
    """
    new_user = await auth_service.register_user(user_data)
    
    # Después del registro exitoso, genera el token
    access_token = auth_service.create_user_token(new_user)
    return {"access_token": access_token, "token_type": "bearer"}

# --- 2. Endpoint de Inicio de Sesión (Token) ---
@router.post("/token", response_model=Token)
async def login_for_access_token(
    # Usa el formulario estándar de OAuth2 para recibir username (email) y password
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Procesa las credenciales (email y password) y devuelve un token JWT.
    """
    # El 'username' de OAuth2PasswordRequestForm se usa para el email
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        # Lanza una excepción 401 que es estándar en el flujo OAuth2
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario no activo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crea el token JWT
    access_token = auth_service.create_user_token(user)
    
    return {"access_token": access_token, "token_type": "bearer"}