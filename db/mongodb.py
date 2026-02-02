from motor.motor_asyncio import AsyncIOMotorClient
import logging

# FIX CRÍTICO: Usamos importación ABSOLUTA desde la raíz del proyecto.
# La carpeta 'config' está al mismo nivel que 'db'.
from config.settings import settings 

# Variables globales para la conexión
client: AsyncIOMotorClient = None
db_client = None

async def connect():
    """Establece la conexión a MongoDB."""
    global client, db_client
    
    logging.info(f"Intentando conectar a MongoDB en: {settings.MONGODB_URI}")
    try:
        # Inicializa el cliente y la base de datos
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000 # Timeout de 5 segundos para fallar rápido
        )
        # Prueba la conexión
        await client.admin.command('ping')
        
        # Asigna la base de datos específica
        db_client = client[settings.MONGODB_DATABASE]
        
        logging.info("Conexión a MongoDB exitosa.")
        
    except Exception as e:
        logging.error(f"Fallo al conectar a MongoDB. Asegúrate de que el servidor esté corriendo. Error: {e}")
        # En un entorno real, podrías querer detener la aplicación aquí

async def close():
    """Cierra la conexión a MongoDB."""
    global client
    if client:
        logging.info("Cerrando conexión a MongoDB.")
        client.close()

# Función helper para obtener la instancia del cliente de la base de datos
# RENOMBRADO A get_db para coincidir con la importación en auth.py
def get_db():
    """Retorna la instancia del cliente de la base de datos (db_client)."""
    if db_client is None:
        # Esto solo debería ocurrir si la aplicación se usa antes de connect()
        raise Exception("La conexión a la base de datos no está inicializada.")
    return db_client