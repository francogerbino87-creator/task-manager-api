from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Clase de configuración de la aplicación.
    Utiliza BaseSettings de Pydantic para cargar variables de entorno
    (o un archivo .env si está configurado).
    """
    
    # --- Configuración General de la API ---
    TITLE: str = Field("Task Manager API", description="Título de la aplicación FastAPI")
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API REST para gestionar tareas, protegida con JWT y MongoDB."

    # --- Configuración de Seguridad JWT ---
    SECRET_KEY: str = Field("tu_clave_secreta_aqui", description="Clave secreta para firmar tokens JWT.")
    ALGORITHM: str = "HS256"
    # Tiempo de expiración del token en minutos (e.g., 30 minutos)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- Configuración de Base de Datos MongoDB ---
    # Nota: URI de conexión, generalmente cargada desde variables de entorno
    # Usa un valor por defecto seguro (aunque probablemente lo cargues desde .env)
    MONGO_URI: str = Field("mongodb://localhost:27017", description="URI de conexión a MongoDB.")
    MONGO_DB_NAME: str = Field("task_manager_db", description="Nombre de la base de datos.")

    # Configuración del modelo:
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )

settings = Settings()