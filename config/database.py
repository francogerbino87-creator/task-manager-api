from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

# Cliente de MongoDB
client = None
# Base de datos específica
db = None

async def connect_to_mongo():
    """Establece la conexión a MongoDB al iniciar la aplicación."""
    global client, db
    print("Conectando a MongoDB...")
    try:
        # Inicializa el cliente asíncrono
        client = AsyncIOMotorClient(settings.MONGO_URI)
        # Selecciona la base de datos
        db = client[settings.MONGO_DB_NAME]
        print("Conexión a MongoDB exitosa.")
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        # En una aplicación real, podrías querer manejar la salida de manera más robusta.

async def close_mongo_connection():
    """Cierra la conexión a MongoDB al apagar la aplicación."""
    global client
    if client:
        client.close()
        print("Conexión a MongoDB cerrada.")

# Función de ayuda para obtener la colección de tareas
def get_task_collection():
    return db.tasks