from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId # Todavía necesario para la validación de IDs en la ruta

# Importación de Repositorio y Dependencias
from repositories.task_repository import TaskRepository
from schemas.task_schema import TaskInDB, TaskCreate, TaskUpdate, TaskListResponse
from schemas.user_schema import UserInDB
from app.core.dependencies import get_current_user, get_task_repository # Importamos el repositorio

# Crea la instancia del router y añade el prefijo para la documentación
router = APIRouter(
    prefix="/tasks",
    tags=["Tareas"],
)

# --- Dependencia Helper para obtener la Tarea o lanzar 404 ---
async def get_task_or_404_by_repo(
    task_id: str, 
    # Inyectamos el usuario actual y el repositorio
    current_user: Annotated[UserInDB, Depends(get_current_user)], 
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)]
) -> TaskInDB:
    """
    Busca una tarea por ID para el usuario actual utilizando el repositorio.
    Lanza HTTPException 404 si no se encuentra o no pertenece al usuario.
    """
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID de tarea inválido")
    
    # El repositorio maneja la lógica de buscar por ID + Owner_ID
    task = await task_repo.get_by_id(task_id, current_user.id)
    
    if not task:
        # Mensaje genérico por seguridad
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
        
    return task


# --- Rutas CRUD (Usando el Repositorio) ---

@router.post("/", response_model=TaskInDB, status_code=status.HTTP_201_CREATED, summary="Crear Tarea")
async def create_task(
    task_in: TaskCreate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
):
    """Crea una nueva tarea para el usuario autenticado."""
    # Delega la creación y asignación de owner_id al repositorio
    new_task = await task_repo.create_task(task_in, current_user.id)
    return new_task

@router.get("/", response_model=TaskListResponse, summary="Listar Tareas")
async def read_tasks(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
):
    """Lista todas las tareas del usuario autenticado."""
    # Por ahora, usamos una lista simple sin paginación (si TaskRepository tiene paginación, 
    # podrías ajustar esto para incluir page y size como query params)
    tasks = await task_repo.get_all_tasks(current_user.id)
    return {"tasks": tasks, "total": len(tasks)}

@router.get("/{task_id}", response_model=TaskInDB, summary="Obtener Tarea por ID")
async def read_task(
    # La dependencia helper ya busca y valida la tarea
    task: Annotated[TaskInDB, Depends(get_task_or_404_by_repo)], 
):
    """Obtiene una tarea específica por su ID, verificando propiedad."""
    return task 

@router.put("/{task_id}", response_model=TaskInDB, summary="Actualizar Tarea")
async def update_task(
    task_update: TaskUpdate,
    # Obtenemos la tarea existente y verificada por la dependencia helper
    task: Annotated[TaskInDB, Depends(get_task_or_404_by_repo)], 
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
):
    """Actualiza una tarea existente."""
    
    # El repositorio maneja la actualización y el timestamp
    updated_task = await task_repo.update_task(task.id, current_user.id, task_update)

    if not updated_task:
        # En caso de que el repositorio falle en encontrarla después de la verificación
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos al actualizar")

    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Tarea")
async def delete_task(
    # Obtenemos la tarea para asegurar que existe antes de intentar borrar
    task: Annotated[TaskInDB, Depends(get_task_or_404_by_repo)], 
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
):
    """Elimina una tarea existente por su ID."""
    
    # El repositorio maneja la eliminación con la verificación de owner_id
    deleted = await task_repo.delete_task(task.id, current_user.id)
    
    if not deleted:
        # Si no se pudo borrar, algo falló a nivel DB/repositorio
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo al eliminar la tarea")
        
    return