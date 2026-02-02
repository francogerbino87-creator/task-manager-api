from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Optional
from bson import ObjectId

from schemas.task_schema import TaskCreate, TaskModel, TaskUpdate, PaginatedTaskResponse
from db.mongodb import get_db # CORREGIDO: Importar desde 'db.mongodb'
from app.core.dependencies import get_current_user
from config.settings import settings # AÑADIDO: Importar settings para el nombre de colección
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
TASKS_COLLECTION = settings.COLLECTION_TASKS # CORREGIDO: Usar el nombre de colección de settings

# --- HELPERS ---

def map_task_model(task: dict) -> TaskModel:
    """Convierte un documento de MongoDB (dict) a un objeto TaskModel."""
    if task:
        # Asegura que el _id de MongoDB se mapee correctamente al campo 'id' de Pydantic
        # Usamos pop para que no haya conflicto con el mapeo del modelo Pydantic
        task['id'] = str(task.pop('_id')) 
    return TaskModel(**task) if task else None

# --- RUTAS CRUD ---

# 1. CREAR TAREA
@router.post("/", response_model=TaskModel, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crea una nueva tarea para el usuario autenticado."""
    db = get_db()
    
    # Excluir campos que serán generados en el servidor
    task_data = task_in.model_dump()
    
    # Asignar metadata y propietario
    # El ID del usuario se obtiene de la dependencia 'current_user'
    task_data["owner_id"] = str(current_user["_id"])
    task_data["completed"] = False
    task_data["created_at"] = datetime.utcnow()
    task_data["updated_at"] = datetime.utcnow()
    
    result = await db[TASKS_COLLECTION].insert_one(task_data)
    
    new_task = await db[TASKS_COLLECTION].find_one({"_id": result.inserted_id})
    
    return map_task_model(new_task)

# 2. LISTAR TAREAS (con Paginación y Filtros)
@router.get("/", response_model=PaginatedTaskResponse[TaskModel])
async def list_tasks(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Número de página."),
    size: int = Query(10, ge=1, le=100, description="Tareas por página."),
    completed: Optional[bool] = Query(None, description="Filtrar por estado de completado.")
):
    """Lista las tareas del usuario, con soporte para paginación y filtros."""
    db = get_db()
    owner_id = str(current_user["_id"])
    
    # 1. Construir el filtro base
    query_filter = {"owner_id": owner_id}
    
    if completed is not None:
        query_filter["completed"] = completed
        
    # 2. Calcular el total (importante para la paginación)
    total_count = await db[TASKS_COLLECTION].count_documents(query_filter)
    
    # 3. Calcular saltos (skip)
    skip = (page - 1) * size
    
    # 4. Obtener los documentos
    # Ordenar por fecha de creación descendente (la más nueva primero)
    cursor = db[TASKS_COLLECTION].find(query_filter).sort("created_at", -1).skip(skip).limit(size)
    tasks = await cursor.to_list(length=size)
    
    # 5. Mapear y devolver
    mapped_tasks = [map_task_model(task) for task in tasks]
    
    return PaginatedTaskResponse(
        items=mapped_tasks,
        total=total_count,
        page=page,
        size=size
    )

# 3. OBTENER TAREA por ID
@router.get("/{task_id}", response_model=TaskModel)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtiene una tarea por su ID, asegurando que pertenezca al usuario autenticado."""
    db = get_db()
    
    try:
        object_id = ObjectId(task_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tarea inválido")
        
    task = await db[TASKS_COLLECTION].find_one({
        "_id": object_id,
        "owner_id": str(current_user["_id"])
    })
    
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada o no pertenece al usuario")
        
    return map_task_model(task)

# 4. ACTUALIZAR TAREA
@router.patch("/{task_id}", response_model=TaskModel)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza campos específicos de una tarea existente."""
    db = get_db()
    
    # 1. Validar el ID
    try:
        object_id = ObjectId(task_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tarea inválido")
        
    # 2. Preparar datos de actualización
    # exclude_unset=True asegura que solo se actualizan los campos presentes en el cuerpo del request
    update_data = task_in.model_dump(exclude_unset=True) 
    
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron datos para actualizar")
        
    update_data["updated_at"] = datetime.utcnow()
    
    # 3. Realizar la actualización, buscando por _id y owner_id
    result = await db[TASKS_COLLECTION].update_one(
        {
            "_id": object_id,
            "owner_id": str(current_user["_id"])
        },
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada o no pertenece al usuario")
    
    # 4. Obtener y devolver la tarea actualizada
    updated_task_doc = await db[TASKS_COLLECTION].find_one({"_id": object_id})
    return map_task_model(updated_task_doc)

# 5. ELIMINAR TAREA
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Elimina una tarea por su ID."""
    db = get_db()
    
    try:
        object_id = ObjectId(task_id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de tarea inválido")
        
    result = await db[TASKS_COLLECTION].delete_one({
        "_id": object_id,
        "owner_id": str(current_user["_id"])
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada o no pertenece al usuario")
    
    # HTTP 204 NO CONTENT no devuelve cuerpo, solo el status
    return