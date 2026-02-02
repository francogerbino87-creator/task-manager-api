from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

# NOTA: Ajustar la ruta base si es necesario. Asumo que '.env' está en la raíz del proyecto.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, '.env')

class Settings(BaseSettings):
    # --- Configuración General del Proyecto ---
    PROJECT_NAME: str = Field("Task Manager API", description="Nombre del proyecto FastAPI.")
    API_VERSION: str = Field("v1", description="Versión de la API.")

    # --- Configuración de Seguridad (JWT) ---
    SECRET_KEY: str = Field(..., description="Clave secreta para firmar tokens JWT.")
    ALGORITHM: str = Field("HS256", description="Algoritmo de codificación JWT.")
    # 7 días
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24 * 7, description="Tiempo de expiración del token.") 

    # --- Configuración de MongoDB ---
    MONGODB_URI: str = Field("mongodb://localhost:27017", description="URI de conexión a MongoDB.")
    MONGODB_DATABASE: str = Field("task_manager_db", description="Nombre de la base de datos a usar.")
    MONGODB_USERS_COLLECTION: str = Field("users", description="Nombre de la colección de usuarios.")
    MONGODB_TASKS_COLLECTION: str = Field("tasks", description="Nombre de la colección de tareas.")

    # El modelo debe leer del archivo .env
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, 
        extra="ignore"
    )

settings = Settings()