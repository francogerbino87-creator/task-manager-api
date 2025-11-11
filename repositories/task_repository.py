from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any

from db.mongodb import mongodb
from schemas.task_schema import TaskInDB
from utils.exceptions import NotFoundException # Asegúrate de tener NotFoundException si lo usas

# Función auxiliar para convertir el documento de MongoDB en un modelo Pydantic
def document_to_task(document: Dict[str, Any]) -> TaskInDB:
    """Convierte un documento de MongoDB a un objeto TaskInDB."""
    # Renombra _id a id para que Pydantic lo mapee correctamente
    return TaskInDB(**document)

class TaskRepository:
    def __init__(self):
        # Obtenemos la colección de 'tasks'
        self.collection = mongodb.db["tasks"]

    async def create(self, task_data: Dict[str, Any]) -> TaskInDB:
        """Crea una nueva tarea."""
        
        # Añade timestamps antes de la inserción
        now = datetime.utcnow()
        task_data["created_at"] = now
        task_data["updated_at"] = now
        
        # El owner_id ya debería estar incluido en task_data
        
        result = await self.collection.insert_one(task_data)
        
        # Recupera el documento recién creado para devolver el TaskInDB completo
        new_task_doc = await self.collection.find_one({"_id": result.inserted_id})
        return document_to_task(new_task_doc)

    async def list_by_owner(self, owner_id: str) -> List[TaskInDB]:
        """Lista todas las tareas que pertenecen a un owner_id específico."""
        
        # Consulta: Solo documentos donde owner_id coincide
        cursor = self.collection.find({"owner_id": owner_id}).sort("created_at", -1)
        tasks = await cursor.to_list(length=100)
        
        return [document_to_task(task) for task in tasks]

    async def get_by_id_and_owner(self, task_id: str, owner_id: str) -> Optional[TaskInDB]:
        """Obtiene una tarea por su ID, verificando que pertenezca al owner_id."""
        try:
            object_id = ObjectId(task_id)
        except:
            return None # ID no válido

        # Consulta: _id debe coincidir Y owner_id debe coincidir
        query = {"_id": object_id, "owner_id": owner_id}
        task_doc = await self.collection.find_one(query)

        if task_doc:
            return document_to_task(task_doc)
        return None

    async def update(self, task_id: str, owner_id: str, update_data: Dict[str, Any]) -> Optional[TaskInDB]:
        """Actualiza una tarea por ID, solo si pertenece al owner_id."""
        try:
            object_id = ObjectId(task_id)
        except:
            return None

        # 1. Definir el filtro: la tarea debe tener este ID Y este owner_id
        filter_query = {"_id": object_id, "owner_id": owner_id}
        
        # 2. Agregar el timestamp de actualización
        update_data["updated_at"] = datetime.utcnow()
        
        # 3. Aplicar la actualización
        result = await self.collection.update_one(
            filter_query,
            {"$set": update_data}
        )

        if result.modified_count == 0:
            return None # Tarea no encontrada o no modificada

        # 4. Obtener la tarea actualizada
        updated_task_doc = await self.collection.find_one({"_id": object_id})
        return document_to_task(updated_task_doc)

    async def delete(self, task_id: str, owner_id: str) -> int:
        """Elimina una tarea por ID, solo si pertenece al owner_id."""
        try:
            object_id = ObjectId(task_id)
        except:
            return 0

        # Definir el filtro: la tarea debe tener este ID Y este owner_id
        filter_query = {"_id": object_id, "owner_id": owner_id}
        
        result = await self.collection.delete_one(filter_query)
        
        # Retorna el número de documentos eliminados (0 o 1)
        return result.deleted_count