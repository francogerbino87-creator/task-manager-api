from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Esquema base para la creación de una tarea (TaskCreate)
# Esto cubre los campos que el usuario envía al crear o que TaskInDB hereda.
class TaskBase(BaseModel):
    title: str = Field(..., max_length=100, example="Completar el informe trimestral")
    description: Optional[str] = Field(None, example="Revisar datos de ventas y preparar gráficos.")
    is_completed: bool = Field(False, example=False)

# Esquema para la CREACIÓN (POST) de una tarea
class TaskCreate(TaskBase):
    pass # No se necesita lógica adicional por ahora

# Esquema para la LECTURA (GET) de una tarea (incluye IDs y timestamps)
class TaskInDB(TaskBase):
    # El id de MongoDB lo mapeamos a 'id' para mayor convención REST
    # Nota: También debe incluir el ID del usuario propietario
    id: str = Field(..., alias="_id", example="60c72b2f9c1e7c001f8d4e5a")
    owner_id: str = Field(..., example="auth-user-id-123") # Nuevo campo: ID del propietario de la tarea
    created_at: datetime 
    updated_at: datetime

    # Configuración para FastAPI/Pydantic
    class Config:
        # Permite mapear alias (e.g., '_id' a 'id')
        populate_by_name = True
        # Permite que el modelo se inicialice a partir de atributos de instancia (e.g. de un objeto PyMongo)
        from_attributes = True 
        # FastAPI convierte el modelo a JSON automáticamente
        json_encoders = {
            # Convertimos datetime a ISO 8601 string para JSON
            datetime: lambda dt: dt.isoformat(),
        }

# Esquema para la ACTUALIZACIÓN (PATCH/PUT)
class TaskUpdate(BaseModel):
    # Todos los campos son opcionales para permitir actualizaciones parciales
    title: Optional[str] = Field(None, max_length=100, example="Completar el informe trimestral V2")
    description: Optional[str] = Field(None, example="Revisar datos de ventas y preparar gráficos (actualizado).")
    is_completed: Optional[bool] = Field(None, example=True)