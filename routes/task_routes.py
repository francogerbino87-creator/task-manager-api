from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from schemas.task_schema import TaskCreate, TaskInDB, TaskUpdate
from repositories.task_repository import TaskRepository
from schemas.user_schema import UserInDB
from dependencies.auth_dependencies import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

# Inyección de dependencia del repositorio
def get_task_repository():
    return TaskRepository()

@router.post("/", response_model=TaskInDB, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: UserInDB = Depends(get_current_user), # Obtenemos el usuario autenticado
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Crea una nueva tarea, asociándola al usuario actual."""
    
    # 1. Creamos el objeto de tarea con el owner_id del usuario actual
    task_data_with_owner = task_data.model_dump()
    task_data_with_owner["owner_id"] = current_user.id
    
    # 2. El repositorio se encarga de insertar y devolver la tarea
    new_task = await task_repo.create(task_data_with_owner)
    
    if not new_task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la tarea en la base de datos."
        )
    return new_task

@router.get("/", response_model=List[TaskInDB])
async def list_tasks(
    current_user: UserInDB = Depends(get_current_user),
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Lista todas las tareas que pertenecen al usuario autenticado."""
    
    # El repositorio usará el owner_id para filtrar las tareas
    return await task_repo.list_by_owner(current_user.id)

@router.get("/{task_id}", response_model=TaskInDB)
async def get_task(
    task_id: str,
    current_user: UserInDB = Depends(get_current_user),
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Obtiene una tarea específica, verificando que pertenezca al usuario actual."""
    
    task = await task_repo.get_by_id_and_owner(task_id, current_user.id)
    
    if task is None:
        # Usamos 404 para no dar pistas sobre si la tarea existe o no (seguridad por opacidad)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada."
        )
    return task

@router.patch("/{task_id}", response_model=TaskInDB)
async def update_task(
    task_id: str, 
    task_update: TaskUpdate,
    current_user: UserInDB = Depends(get_current_user),
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Actualiza una tarea, verificando que pertenezca al usuario actual."""
    
    # Actualizamos solo si el ID de la tarea y el owner_id coinciden
    updated_task = await task_repo.update(task_id, current_user.id, task_update.model_dump(exclude_unset=True))
    
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no tienes permiso para actualizarla."
        )
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: UserInDB = Depends(get_current_user),
    task_repo: TaskRepository = Depends(get_task_repository)
):
    """Elimina una tarea, verificando que pertenezca al usuario actual."""
    
    deleted_count = await task_repo.delete(task_id, current_user.id)
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no tienes permiso para eliminarla."
        )
    return