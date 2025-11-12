from typing import List, TypeVar, Generic, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
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
    pass 

# 3. Schema para la actualización de tareas
class TaskUpdate(BaseModel):
    # FIX: Todos los campos opcionales deben tener '= None'
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_field(cls, values):
        """Asegura que al menos un campo sea proporcionado para la actualización."""
        if not values:
            raise ValueError("Debe proporcionar al menos un campo para actualizar la tarea.")
        return values

# 4. Schema del modelo completo (como se almacena y se devuelve)
class TaskModel(TaskBase):
    # FIX: Aseguramos que los campos Optional tengan '= None'
    id: Optional[str] = Field(None, alias="_id", description="ID de la tarea en MongoDB.")
    owner_id: str = Field(..., description="ID del usuario propietario de la tarea.")
    completed: bool = Field(False, description="Estado de la tarea.")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación.")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última fecha de actualización.")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

# 5. Esquema de Paginación (Genérico)
class PaginatedTaskResponse(BaseModel, Generic[T]): 
    """Esquema para la respuesta de tareas paginadas."""
    items: List[T] = Field(..., description="Lista de elementos en la página actual.")
    total: int = Field(..., description="Número total de elementos encontrados.")
    page: int = Field(..., description="Número de página actual.")
    size: int = Field(..., description="Número de elementos por página.")