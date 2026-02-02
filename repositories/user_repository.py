from typing import Optional, List, Dict, Any
# CRÍTICO: Usar AsyncIOMotorDatabase para el tipo de la base de datos
from motor.motor_asyncio import AsyncIOMotorDatabase 
from bson import ObjectId

# Importamos verify_password y get_password_hash (si se usa)
from app.core.security import verify_password # Se mantiene la ruta absoluta
from config.settings import settings # CORREGIDO: Usamos 'config.settings'

from schemas.user_schema import UserCreate, UserInDB

# Usamos la clave de configuración correcta para la colección de usuarios
USERS_COLLECTION = settings.MONGODB_USERS_COLLECTION

class UserRepository:
    """
    Repositorio de acceso a datos para la colección de Usuarios.
    """
    # CRÍTICO: Cambiamos AsyncIOMotorClient a AsyncIOMotorDatabase
    def __init__(self, db: AsyncIOMotorDatabase):
        """Inicializa el repositorio con la colección de usuarios."""
        self.db = db
        self.collection = db[USERS_COLLECTION]

    def _convert_doc(self, doc: Dict[str, Any]) -> Optional[UserInDB]:
        """Convierte el documento de MongoDB a UserInDB Pydantic model."""
        if doc:
            # Reemplaza _id con 'id' y asegura que se pueda instanciar UserInDB
            doc['id'] = str(doc.pop('_id'))
            return UserInDB(**doc)
        return None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Obtiene un usuario por su ID (string)."""
        if not ObjectId.is_valid(user_id):
            return None
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._convert_doc(user_doc)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Obtiene un usuario por su correo electrónico."""
        user_doc = await self.collection.find_one({"email": email})
        return self._convert_doc(user_doc)

    async def create_user(self, user_in: UserCreate, hashed_password: str) -> UserInDB:
        """
        Crea un nuevo usuario en la base de datos con una contraseña ya hasheada.
        """
        
        # 1. Repetimos la verificación por seguridad de la DB
        if await self.get_by_email(user_in.email):
            # En un repo, es mejor lanzar una excepción para que el servicio la capture
            raise ValueError("Email already registered") 

        # 2. Preparar el documento para MongoDB
        user_data = user_in.model_dump(exclude={"password"}, exclude_none=True)
        user_data["hashed_password"] = hashed_password
        user_data["is_active"] = True # Por defecto activo
        
        # 3. Insertar en MongoDB
        result = await self.collection.insert_one(user_data)
        
        # 4. Recuperar el documento insertado
        created_user_doc = await self.collection.find_one({"_id": result.inserted_id})
        
        if not created_user_doc:
            raise Exception("Failed to retrieve created user document after insertion.")
            
        return self._convert_doc(created_user_doc)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica la contraseña (usa la función de utilidad)."""
        return verify_password(plain_password, hashed_password)