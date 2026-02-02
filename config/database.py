from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import AsyncGenerator, Optional
from fastapi import Depends

# Importamos las configuraciones creadas en config/settings.py
from config.settings import settings

# Variable global para el cliente de MongoDB
client: Optional[AsyncIOMotorClient] = None

# --- Funciones de Ciclo de Vida (Startup/Shutdown) ---

async def connect_to_mongo():
    """Establece la conexión al inicio del servidor."""
    global client
    print(f"INFO: Intentando conectar a MongoDB en {settings.MONGODB_URI}...")
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000, # 5 segundos de timeout
            uuidRepresentation="standard" # Recomendado para FastAPI/Pydantic
        )
        # Intenta una conexión para verificar que el servidor esté disponible
        await client.admin.command('ping')
        print(f"INFO: Conexión a MongoDB exitosa a la base de datos '{settings.MONGODB_DATABASE}'.")
    except Exception as e:
        print(f"ERROR: No se pudo conectar a MongoDB. Asegúrate de que el servidor esté corriendo.")
        print(f"Detalles del error: {e}")
        # En una aplicación real, se podría detener el servicio aquí
        # raise Exception("Fallo en la conexión a la base de datos")

async def close_mongo_connection():
    """Cierra la conexión al apagar el servidor."""
    global client
    if client:
        client.close()
        print("INFO: Conexión a MongoDB cerrada.")

# --- Dependencia de FastAPI ---

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Función de dependencia para inyectar la base de datos a las rutas de FastAPI.
    """
    global client
    if client is None:
        # En caso de que la conexión inicial fallara o no se haya llamado connect_to_mongo
        await connect_to_mongo() 
        if client is None:
             raise Exception("Cliente de MongoDB no disponible.")

    # El cliente de motor es un objeto Thread-safe, se puede usar en la dependencia
    # Retorna la base de datos específica configurada
    db = client[settings.MONGODB_DATABASE]
    
    try:
        yield db
    finally:
        # No cerramos la conexión aquí, sino al apagar el servidor
        pass

# Renombramos get_db a get_database por si el código antiguo lo usaba, pero 
# se recomienda usar solo get_db para evitar confusiones.
get_database = get_db