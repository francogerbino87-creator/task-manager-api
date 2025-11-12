from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config.settings import settings
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definimos variables globales para la conexión y la base de datos
# client: Será la instancia del cliente Motor para MongoDB
# database: Será la instancia de la base de datos específica
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """
    Inicializa la conexión a MongoDB usando el URI de las settings.
    Se ejecuta durante el evento 'startup' de FastAPI.
    """
    global client, database
    
    try:
        # Crea la conexión asíncrona a MongoDB
        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000  # Tiempo máximo de espera para la conexión
        )
        # Selecciona la base de datos especificada en settings
        database = client[settings.MONGO_DB_NAME]
        
        # Intenta verificar la conexión
        await client.admin.command('ping')
        logger.info(f"Conexión exitosa a MongoDB en URI: {settings.MONGO_URI}")
        
    except Exception as e:
        logger.error(f"Fallo al conectar a MongoDB: {e}")
        # En una aplicación real, podrías querer terminar la aplicación aquí.
        # Por ahora, solo registramos el error.


async def close_mongo_connection():
    """
    Cierra la conexión con el cliente de MongoDB.
    Se ejecuta durante el evento 'shutdown' de FastAPI.
    """
    global client
    if client:
        client.close()
        logger.info("Conexión a MongoDB cerrada.")

# Función de utilidad para obtener la base de datos (útil para inyección de dependencia)
def get_database() -> AsyncIOMotorDatabase:
    """Devuelve la instancia de la base de datos MongoDB."""
    if database is None:
        raise Exception("Database client not initialized. Call connect_to_mongo first.")
    return database