from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
# CRÍTICO: Importar desde el nombre de archivo correcto: 'config.settings'
from config.settings import settings 
# CRÍTICO: Importar las funciones de conexión de base de datos desde la ubicación correcta
from config.database import connect_to_mongo, close_mongo_connection
# Asume que tus carpetas de rutas están al mismo nivel que app/
from routes import auth_routes, task_routes, user_routes

# --- Configuración del Router Principal (Agregador) ---

# Creamos un router principal que encapsulará todas las rutas de la API (v1)
api_router = APIRouter()

# 1. Rutas de Autenticación
api_router.include_router(auth_routes.router)

# 2. Rutas de Tareas
api_router.include_router(task_routes.router)

# 3. Rutas de Usuarios
api_router.include_router(user_routes.router) 


# --- Inicialización de la Aplicación FastAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Crear la instancia de la aplicación
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# --- Montar el Router Principal en la Aplicación ---

# Se monta el router principal, agregando el prefijo '/api/v1' a todas las rutas.
app.include_router(api_router, prefix="/api/v1")


# --- Ruta de Salud (Health Check) ---
@app.get("/", tags=["Health Check"], summary="Verificar estado del servidor")
async def root():
    """Ruta simple para verificar que el servidor esté funcionando."""
    return {"message": f"{settings.PROJECT_NAME} - API {settings.API_VERSION} is running!"}