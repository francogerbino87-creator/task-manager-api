from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

# Base schema for shared attributes
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico único del usuario.")
    full_name: Optional[str] = None
    
# Schema for user registration (includes the plain password)
class UserCreate(UserBase):
    password: str = Field(..., description="Contraseña del usuario (texto plano).")

# Schema representing a user in the database
class UserInDBBase(UserBase):
    id: Optional[str] = Field(None, alias="_id", description="ID de MongoDB (ObjectId en string).") 
    
    # Configuración de Pydantic v2
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class UserInDB(UserInDBBase):
    hashed_password: str = Field(..., description="Contraseña hasheada para almacenamiento seguro.")
    # Usamos string 'TaskModel' para evitar la importación circular inicial
    tasks: Optional[List['TaskModel']] = None 

class UserPublic(UserInDBBase):
    tasks: Optional[List['TaskModel']] = None 

# --- Esquemas de Autenticación (JWT) ---

class Token(BaseModel):
    access_token: str = Field(..., description="El token de acceso JWT.")
    token_type: str = Field("bearer", description="El tipo de esquema de autenticación (siempre 'bearer').")

class TokenData(BaseModel):
    sub: Optional[str] = None 
    
# Importa la TaskModel solo para poder resolver la referencia
from schemas.task_schema import TaskModel 

# Resuelve la referencia circular (Pydantic v2 style)
UserInDB.model_rebuild()
UserPublic.model_rebuild()