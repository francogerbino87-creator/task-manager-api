from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import Depends
from config.settings import settings
from schemas.task_schema import TaskModel, TaskCreate, TaskUpdate, PaginatedTaskResponse
from db.mongodb import get_database
from datetime import datetime


class TaskRepository:
    """
    Clase que encapsula la lógica de acceso a datos para la colección de Tareas.
    """
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):
        """Inicializa el repositorio con la colección de tareas."""
        self.collection = db[settings.COLLECTION_TASKS]

    # --- Operaciones de Lectura (Read) ---

    async def get_all_tasks(self, owner_id: str, page: int = 1, size: int = 10) -> PaginatedTaskResponse[TaskModel]:
        """
        Obtiene todas las tareas para un usuario específico con paginación.
        """
        skip = (page - 1) * size
        
        # 1. Filtro para obtener solo las tareas del propietario
        query = {"owner_id": owner_id}

        # 2. Obtener el total de documentos para la paginación
        total_tasks = await self.collection.count_documents(query)

        # 3. Obtener los documentos de la página actual
        # Ordenamos por fecha de creación descendente por defecto
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(size)
        
        tasks_list = []
        async for doc in cursor:
            # Convertir de MongoDB doc a Pydantic model
            doc['id'] = str(doc.pop('_id'))
            tasks_list.append(TaskModel(**doc))

        return PaginatedTaskResponse[TaskModel](
            items=tasks_list,
            total=total_tasks,
            page=page,
            size=size
        )

    async def get_by_id(self, task_id: str, owner_id: str) -> Optional[TaskModel]: # Corregido a Optional[TaskModel]
        """
        Busca una tarea por su ID, asegurando que pertenezca al propietario.
        """
        if not ObjectId.is_valid(task_id):
            return None
            
        task_doc = await self.collection.find_one({
            "_id": ObjectId(task_id),
            "owner_id": owner_id
        })
        
        if task_doc:
            task_doc['id'] = str(task_doc.pop('_id'))
            return TaskModel(**task_doc)
        return None

    # --- Operaciones de Creación (Create) ---

    async def create_task(self, task: TaskCreate, owner_id: str) -> TaskModel:
        """
        Crea una nueva tarea, asignándola al usuario propietario.
        """
        task_data = task.model_dump(exclude_unset=True)
        task_data["owner_id"] = owner_id
        
        # El modelo TaskModel maneja los campos created_at y updated_at
        task_model = TaskModel(**task_data)
        
        # Convertir el modelo a dict para inserción, usando el alias para _id
        insert_data = task_model.model_dump(by_alias=True, exclude_none=True)
        
        # MongoDB se encarga de asignar el _id
        del insert_data["id"] 

        insert_result = await self.collection.insert_one(insert_data)
        
        # Recuperar el documento insertado
        new_task_doc = await self.collection.find_one({"_id": insert_result.inserted_id})
        
        new_task_doc['id'] = str(new_task_doc.pop('_id'))
        return TaskModel(**new_task_doc)

    # --- Operaciones de Actualización (Update) ---

    async def update_task(self, task_id: str, owner_id: str, update_data: TaskUpdate) -> Optional[TaskModel]: # Corregido a Optional[TaskModel]
        """
        Actualiza los campos de una tarea, asegurando la propiedad.
        """
        if not ObjectId.is_valid(task_id):
            return None