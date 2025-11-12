from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, EmailStr
from typing import Optional

# Clase BaseSettings que carga variables de entorno automáticamente
class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.
    Usa el archivo .env en el directorio raíz.
    """
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )

    # --- Configuración General ---
    TITLE: str = "Task Manager API"
    
    # --- Configuración de Seguridad (JWT) ---
    SECRET_KEY: str = Field(..., description="Clave secreta para firmar tokens JWT.")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token expira en 30 minutos

    # --- Configuración de MongoDB ---
    # Usaremos el esquema de conexión asíncrona de MongoDB (Motor)
    MONGO_URI: str = Field(..., description="URI de conexión a MongoDB.")
    MONGO_DB_NAME: str = "task_manager_db"
    
    # Nombres de las colecciones
    COLLECTION_USERS: str = "users"
    COLLECTION_TASKS: str = "tasks"

# Instancia de la configuración
settings = Settings()