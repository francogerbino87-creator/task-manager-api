from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient

# Asume que tienes un archivo de configuración para obtener la URI de MongoDB
from config.settings import settings

# Inicialización de la base de datos y el cliente de MongoDB
# Usaremos 'client' y 'db' para el manejo global de la conexión
client: AsyncIOMotorClient = None
db = None

async def connect_to_mongo():
    """
    Establece la conexión al cliente de MongoDB usando la URI de las settings.
    Se ejecuta al iniciar la aplicación.
    """
    global client, db
    print("Conectando a MongoDB...")
    
    # CRÍTICO: Asegúrate de que settings.MONGO_URI y settings.MONGO_DB_NAME estén configuradas.
    client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    db = client[settings.MONGO_DB_NAME]
    
    try:
        # Intenta obtener información del servidor para verificar la conexión
        await client.admin.command('ping')
        print("Conexión a MongoDB exitosa.")
    except Exception as e:
        print(f"ERROR: Fallo al conectar a MongoDB: {e}")
        # Si la conexión falla, la aplicación continuará, pero la DB estará inaccesible.

async def close_mongo_connection():
    """
    Cierra la conexión al cliente de MongoDB.
    Se ejecuta al detener la aplicación.
    """
    global client
    if client:
        print("Cerrando conexión a MongoDB...")
        client.close()
        print("Conexión a MongoDB cerrada.")

async def get_db() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """
    Dependencia de FastAPI para obtener la instancia de la base de datos.
    """
    global db
    if db is None:
        # En caso de que se llame antes de la conexión, intenta conectar (esto no debería pasar).
        await connect_to_mongo() 

    # 'yield' devuelve la instancia de la base de datos y la mantiene viva.
    yield db