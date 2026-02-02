from typing import Optional
from pydantic import BaseModel, Field, EmailStr

# Esquema base para los datos de entrada
class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., min_length=8, max_length=72, example="securepassword123")
    full_name: Optional[str] = Field(None, example="John Doe")

# Esquema usado para los datos almacenados en la base de datos y para respuestas
class UserInDB(BaseModel):
    # CRÍTICO: Usamos 'id' para Python/FastAPI, y 'alias="_id"' para decirle a Pydantic
    # que cuando vea '_id' en la base de datos, lo llame 'id'.
    id: Optional[str] = Field(None, alias="_id") 
    email: EmailStr
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    
    # CRÍTICO PARA PYDANTIC V2 Y MONGODB
    # Esta configuración es esencial para que Pydantic acepte datos de MongoDB
    # donde los campos se llaman por su nombre de base de datos (p.ej., '_id')
    model_config = {
        "populate_by_name": True, # Permite que se usen los alias
        "json_schema_extra": {
            "example": {
                "id": "60c72b2f9b1d8e001f8b4567",
                "email": "test@example.com",
                "full_name": "Test User",
                "hashed_password": "$2b$12$...",
                "is_active": True
            }
        },
    }
    
# Esquema para la respuesta después del registro (no incluye el hash)
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

# Esquema para la respuesta de inicio de sesión
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"