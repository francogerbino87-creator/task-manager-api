

import sys
import os


# Agregando el path para la correcta importación de módulos (si es necesario)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from config.settings import settings

# 1. IMPORTAR SCHEMAS y RESOLVER CICLOS PRIMERO.
from schemas.task_schema import TaskModel
from schemas.user_schema import UserInDB 

# 2. RESOLUCIÓN DE REFERENCIAS CIRCULARES DE PYDANTIC V2.
# Esto es CRUCIAL y debe ocurrir antes de importar los routers.
TaskModel.model_rebuild()
UserInDB.model_rebuild()

# 3. IMPORTAR ROUTERS AHORA que los modelos están listos.
from routes import task_routes, auth_routes 

from db.mongodb import connect_to_mongo, close_mongo_connection


app = FastAPI(
    title=settings.TITLE, 
    description="API para gestión de tareas con autenticación",
    version="1.0.0"
)

# --- 4. Inclusión de Routers ---
app.include_router(auth_routes.router)
app.include_router(task_routes.router)


# --- Eventos de Conexión ---
@app.on_event("startup")
async def startup_db_client():
    """Conecta a MongoDB al iniciar la aplicación."""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Cierra la conexión a MongoDB al apagar la aplicación."""
    await close_mongo_connection()







@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a Task Manager API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Verificación de salud simple del servidor."""
    return {"status": "healthy"}