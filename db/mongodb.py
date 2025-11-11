from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from motor.core import AgnosticClient, AgnosticDatabase

# Variable global para almacenar la instancia de la base de datos (NO del cliente)
# Usamos 'AgnosticDatabase' para tipar la base de datos específica.
mongodb: AgnosticDatabase | None = None

async def connect_to_mongo():
    """Conecta a MongoDB usando las configuraciones de la aplicación."""
    global mongodb
    try:
        # Inicializa el cliente Motor.
        # Motor Client es la interfaz principal.
        client: AgnosticClient = AsyncIOMotorClient(
            settings.MONGO_URI, 
            serverSelectionTimeoutMS=5000
        )
        
        # Asigna la base de datos específica al objeto global 'mongodb'.
        # Esto es lo que se importa como 'mongodb' en los repositorios.
        mongodb = client[settings.MONGO_DB_NAME] 
        
        # Comando de prueba para asegurar que la conexión está activa.
        await client.admin.command('ping')
        print("Conexión a MongoDB exitosa.")
    except Exception as e:
        # Si la conexión falla, imprimimos el error y detenemos la aplicación.
        print(f"Error al conectar a MongoDB: {e}")
        # En un entorno de producción, aquí se podría lanzar una excepción que detenga el arranque de FastAPI.
        
async def close_mongo_connection():
    """Cierra la conexión de MongoDB."""
    global mongodb
    if mongodb:
        # MotorDatabase tiene una referencia al cliente subyacente que se puede cerrar.
        # Verificamos si la instancia tiene un cliente que podemos cerrar.
        if hasattr(mongodb, 'client') and mongodb.client:
            mongodb.client.close()
            print("Conexión a MongoDB cerrada.")
        # Si mongodb es solo la base de datos, no tiene un método close directo,
        # pero su cliente sí. La lógica anterior debería ser suficiente.

# Nota: El tipo 'AgnosticDatabase' se usa para tipado, ya que el objeto 'mongodb' es la base de datos.