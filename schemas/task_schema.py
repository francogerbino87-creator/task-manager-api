from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar('T')
 
# 1. Schema Base para atributos compartidos
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Título de la tarea.")
    # FIX: Se añade '= None' a los campos Optional para compatibilidad con OpenAPI
    description: Optional[str] = None 
    due_date: Optional[datetime] = None 

# 2. Schema para la creación de una nueva tarea
class TaskCreate(TaskBase):
    pass # Hereda todos los campos de TaskBase

# 3. Schema para la actualización de tareas
class TaskUpdate(BaseModel):
    # Todos los campos deben ser opcionales y tener valor None
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Completar la migración de dependencias",
                "completed": True
            }
        }
    }

# 4. Schema del modelo completo (como se almacena y se devuelve)
class TaskInDB(TaskBase):
    id: str = Field(..., description="ID de la tarea en MongoDB.")
    owner_id: str = Field(..., description="ID del usuario propietario de la tarea.")
    completed: bool = Field(False, description="Estado de la tarea.")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat() if dt else None
        }
    )

# 5. Schema para respuesta paginada de tareas
class TaskListResponse(BaseModel):
    tasks: List[TaskInDB]
    total: int = 0
    page: int = 1
    size: int = 10