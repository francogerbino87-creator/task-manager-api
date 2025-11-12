from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import Depends
from config.settings import settings
from schemas.user_schema import UserCreate, UserInDB
from services.auth_service import get_password_hash
from db.mongodb import get_database

class UserRepository:
    """
    Clase que encapsula la lógica de acceso a datos para la colección de Usuarios.
    """
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):
        """Inicializa el repositorio con la colección de usuarios."""
        self.collection = db[settings.COLLECTION_USERS]

    async def create_user(self, user: UserCreate) -> UserInDB:
        """
        Crea un nuevo usuario, hasheando la contraseña antes de insertarlo.
        """
        # 1. Hashear la contraseña
        hashed_password = get_password_hash(user.password)
        
        # 2. Convertir el esquema de creación a un diccionario para MongoDB
        user_data = user.model_dump(exclude_unset=True, by_alias=False)
        user_data["hashed_password"] = hashed_password
        
        # 3. Eliminar la contraseña plana antes de la inserción
        del user_data["password"]
        
        # 4. Insertar el documento en MongoDB
        insert_result = await self.collection.insert_one(user_data)
        
        # 5. Recuperar el documento insertado (necesario para obtener el _id)
        new_user_doc = await self.collection.find_one({"_id": insert_result.inserted_id})

        # 6. Convertir el documento a la estructura UserInDB
        # El documento de MongoDB usa '_id', pero el modelo Pydantic espera 'id'.
        new_user_doc['id'] = str(new_user_doc.pop('_id'))
        
        return UserInDB(**new_user_doc)

    async def get_by_email(self, email: str) -> Optional[UserInDB]: # Corregido a Optional[UserInDB]
        """Busca un usuario por su dirección de email."""
        user_doc = await self.collection.find_one({"email": email})
        
        if user_doc:
            # Convertir de MongoDB doc a Pydantic model
            user_doc['id'] = str(user_doc.pop('_id'))
            return UserInDB(**user_doc)
        
        return None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]: # Corregido a Optional[UserInDB]
        """Busca un usuario por su ID (ObjectId)."""
        if not ObjectId.is_valid(user_id):
            return None
            
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        
        if user_doc:
            # Convertir de MongoDB doc a Pydantic model
            user_doc['id'] = str(user_doc.pop('_id'))
            return UserInDB(**user_doc)
        
        return None