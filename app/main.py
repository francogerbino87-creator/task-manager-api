from repositories.task_repository import TaskRepository

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from config.settings import settings
from db.mongodb import connect_to_mongo, close_mongo_connection
from routes import task_routes 
from routes import auth_routes

app = FastAPI(
    title=settings.TITLE, # Podrías añadir TITLE a settings.py si quieres
    description="API para gestión de tareas con autenticación",
    version="1.0.0"
)

# --- Eventos de Conexión ---
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
# ---------------------------

# --- Inclusión de Routers ---
app.include_router(task_routes.router)
app.include_router(auth_routes.router)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a Task Manager API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    # En un check real, deberíamos verificar también la conexión a DB
    # Pero por ahora, basta con el estado del servidor
    return {"status": "healthy"}