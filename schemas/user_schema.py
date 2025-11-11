from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# --- Esquemas de Usuario ---

class UserCreate(BaseModel):
    """Esquema usado para el registro de un nuevo usuario."""
    email: EmailStr = Field(..., example="usuario@ejemplo.com")
    password: str = Field(..., min_length=8)

class UserInDB(BaseModel):
    """Esquema de usuario tal como se almacena/lee en la base de datos."""
    id: str = Field(..., alias="_id", example="60c72b2f9c1e7c001f8d4e5b")
    email: EmailStr
    hashed_password: str # Almacenamos el hash, no la contraseña
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

# --- Esquemas de Autenticación ---

class Token(BaseModel):
    """Esquema para la respuesta de login (el token JWT)."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Esquema para los datos decodificados del token (ej. el ID de usuario)."""
    user_id: Optional[str] = None