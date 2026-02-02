from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

# Importamos las configuraciones de la nueva ubicación
# El archivo es 'config/settings.py' y la variable es 'settings'
from config.settings import settings 

# Importamos los esquemas
from schemas.task_schema import TaskInDB, TaskCreate, TaskUpdate 

# Usamos la clave de configuración correcta
TASKS_COLLECTION = settings.MONGODB_TASKS_COLLECTION

class TaskRepository:
    """Clase que encapsula la lógica de acceso a datos para la colección de Tareas."""
    
    # El repositorio recibe la instancia de la base de datos (db) directamente
    # La inyección de dependencia 'Depends(get_database)' se realiza en la función de factory 
    # de las rutas, no aquí.
    def __init__(self, db: AsyncIOMotorDatabase):
        """Inicializa el repositorio con la colección de tareas."""
        self.collection = db[TASKS_COLLECTION] 

    def _convert_doc(self, doc: Dict[str, Any]) -> Optional[TaskInDB]:
        """Convierte el documento de MongoDB a TaskInDB Pydantic model."""
        if doc:
            # Reemplaza _id con 'id' y asegura que se pueda instanciar TaskInDB
            doc['id'] = str(doc.pop('_id'))
            return TaskInDB(**doc)
        return None

    # --- Operaciones de Lectura (Read) ---

    async def get_all_tasks(self, owner_id: str, page: int = 1, size: int = 10) -> List[TaskInDB]:
        """
        Obtiene todas las tareas para un usuario específico con paginación.
        """
        skip = (page - 1) * size
        
        query = {"owner_id": owner_id}

        # Consulta y aplicación de paginación
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(size)
        
        tasks_list = []
        # Usamos to_list para consumir el cursor de manera eficiente con motor
        for doc in await cursor.to_list(length=size):
            tasks_list.append(self._convert_doc(doc))
        
        # Retorna la lista de tareas (sin el objeto de paginación completo por ahora)
        return tasks_list


    async def get_by_id(self, task_id: str, owner_id: str) -> Optional[TaskInDB]: 
        """
        Busca una tarea por su ID, asegurando que pertenezca al propietario.
        """
        if not ObjectId.is_valid(task_id):
            return None
            
        task_doc = await self.collection.find_one({
            "_id": ObjectId(task_id),
            "owner_id": owner_id
        })
        
        return self._convert_doc(task_doc)

    # --- Operaciones de Creación (Create) ---

    async def create_task(self, task: TaskCreate, owner_id: str) -> TaskInDB:
        """
        Crea una nueva tarea, asignándola al usuario propietario.
        """
        now = datetime.utcnow()
        task_data = task.model_dump(exclude_unset=True)
        
        # Añadir campos de control
        task_data.update({
            "owner_id": owner_id,
            "created_at": now,
            "updated_at": now,
        })
        
        insert_result = await self.collection.insert_one(task_data)
        
        # Recuperar el documento insertado
        new_task_doc = await self.collection.find_one({"_id": insert_result.inserted_id})
        
        return self._convert_doc(new_task_doc)


    # --- Operaciones de Actualización (Update) ---

    async def update_task(self, task_id: str, owner_id: str, update_data: TaskUpdate) -> Optional[TaskInDB]: 
        """
        Actualiza los campos de una tarea, asegurando la propiedad.
        """
        if not ObjectId.is_valid(task_id):
            return None
            
        # 1. Preparar los datos de actualización
        update_fields = update_data.model_dump(exclude_unset=True)
        
        if not update_fields:
            # Si no hay campos para actualizar, retornar la tarea existente
            return await self.get_by_id(task_id, owner_id)

        # 2. Añadir marca de tiempo de actualización
        update_fields["updated_at"] = datetime.utcnow()
        
        # 3. Realizar la actualización
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id), "owner_id": owner_id},
            {"$set": update_fields}
        )

        if result.modified_count == 0 and result.matched_count == 0:
            return None # No se encontró la tarea o no es del propietario

        # 4. Recuperar y retornar el documento actualizado
        return await self.get_by_id(task_id, owner_id)

    # --- Operaciones de Eliminación (Delete) ---
    
    async def delete_task(self, task_id: str, owner_id: str) -> bool:
        """
        Elimina una tarea, asegurando la propiedad, y retorna True si fue eliminada.
        """
        if not ObjectId.is_valid(task_id):
            return False
            
        result = await self.collection.delete_one({
            "_id": ObjectId(task_id), 
            "owner_id": owner_id
        })
        
        return result.deleted_count > 0