from typing import Optional
from bson import ObjectId
from datetime import datetime

from config.database import db # Importamos la instancia de la base de datos
from schemas.user_schema import UserCreate, UserInDB

class UserRepository:
    """
    Capa de acceso a datos para la colección de usuarios en MongoDB.
    """
    def __init__(self):
        # Referencia a la colección 'users' en MongoDB
        self.collection = db.users 

    async def create(self, user_data: UserCreate, hashed_password: str) -> UserInDB:
        """Crea un nuevo usuario en la base de datos."""
        
        # 1. Prepara el documento a insertar
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()

        # 2. Inserta en MongoDB
        result = await self.collection.insert_one(user_dict)
        
        # 3. Recupera el usuario insertado (o usa el documento original con el ID)
        inserted_user = await self.collection.find_one({"_id": result.inserted_id})
        
        # 4. Devuelve el modelo tipado
        return UserInDB(**inserted_user)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Busca un usuario por su dirección de correo electrónico."""
        user_doc = await self.collection.find_one({"email": email})
        
        if user_doc:
            # Devuelve el modelo tipado
            return UserInDB(**user_doc)
        
        return None
    
    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Busca un usuario por su ID de MongoDB."""
        if not ObjectId.is_valid(user_id):
            return None
            
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        
        if user_doc:
            return UserInDB(**user_doc)
            
        return None