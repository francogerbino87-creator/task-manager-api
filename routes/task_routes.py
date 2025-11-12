from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated

from schemas.task_schema import TaskModel, TaskCreate, TaskUpdate, PaginatedTaskResponse
from repositories.task_repository import TaskRepository
from services.auth_service import get_current_user_id

# Crea una instancia de APIRouter con el prefijo /tasks y tags para Swagger
router = APIRouter(
    prefix="/tasks",
    tags=["Tareas"],
)

# Dependencia para obtener una instancia del repositorio de tareas
def get_task_repository(repo: TaskRepository = Depends(TaskRepository)):
    """Inyecta la dependencia del repositorio de tareas."""
    return repo

# Dependencia para obtener el ID del usuario actual
# Utilizamos la dependencia de auth_service para proteger todas las rutas de tareas
CurrentUser = Annotated[str, Depends(get_current_user_id)]
TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]

# ----------------------------------------------------
# 1. CREAR TAREA (POST /tasks)
# ----------------------------------------------------
@router.post(
    "/",
    response_model=TaskModel,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nueva tarea"
)
async def create_task_endpoint(
    task_data: TaskCreate,
    current_user_id: CurrentUser,
    task_repo: TaskRepo
):
    """
    Crea una nueva tarea y la asocia al ID del usuario autenticado.
    """
    # Llama al repositorio para crear la tarea
    new_task = await task_repo.create_task(task_data, current_user_id)
    return new_task

# ----------------------------------------------------
# 2. OBTENER TODAS LAS TAREAS (GET /tasks)
# ----------------------------------------------------
@router.get(
    "/",
    response_model=PaginatedTaskResponse[TaskModel],
    summary="Obtiene todas las tareas del usuario actual"
)
async def get_all_tasks_endpoint(
    current_user_id: CurrentUser,
    task_repo: TaskRepo,
    page: int = Query(1, ge=1, description="Número de página para la paginación."),
    size: int = Query(10, ge=1, le=100, description="Número de tareas por página.")
):
    """
    Obtiene todas las tareas del usuario actual, con opciones de paginación.
    """
    # Llama al repositorio para obtener las tareas paginadas
    tasks_response = await task_repo.get_all_tasks(current_user_id, page, size)
    return tasks_response

# ----------------------------------------------------
# 3. OBTENER TAREA POR ID (GET /tasks/{task_id})
# ----------------------------------------------------
@router.get(
    "/{task_id}",
    response_model=TaskModel,
    summary="Obtiene una tarea específica por ID"
)
async def get_task_by_id_endpoint(
    task_id: str,
    current_user_id: CurrentUser,
    task_repo: TaskRepo
):
    """
    Busca y devuelve una tarea por su ID, verificando que pertenezca al usuario autenticado.
    """
    task = await task_repo.get_by_id(task_id, current_user_id)
    
    if task is None:
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no pertenece al usuario."
        )
    return task

# ----------------------------------------------------
# 4. ACTUALIZAR TAREA (PATCH /tasks/{task_id})
# ----------------------------------------------------
@router.patch(
    "/{task_id}",
    response_model=TaskModel,
    summary="Actualiza una tarea existente"
)
async def update_task_endpoint(
    task_id: str,
    update_data: TaskUpdate,
    current_user_id: CurrentUser,
    task_repo: TaskRepo
):
    """
    Actualiza los campos de una tarea por su ID, verificando la propiedad.
    Permite actualizar el título, descripción y estado de completitud.
    """
    updated_task = await task_repo.update_task(task_id, current_user_id, update_data)
    
    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no pertenece al usuario."
        )
    return updated_task

# ----------------------------------------------------
# 5. ELIMINAR TAREA (DELETE /tasks/{task_id})
# ----------------------------------------------------
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina una tarea existente"
)
async def delete_task_endpoint(
    task_id: str,
    current_user_id: CurrentUser,
    task_repo: TaskRepo
):
    """
    Elimina una tarea por su ID, verificando que pertenezca al usuario autenticado.
    Retorna un estado 204 No Content si la eliminación es exitosa.
    """
    success = await task_repo.delete_task(task_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada o no pertenece al usuario."
        )
    # Retorna None con status 204, lo que indica éxito sin cuerpo de respuesta.
    return None