from pydantic import BaseModel
from typing import Optional

class TokenData(BaseModel):
    """
    Esquema para el payload de un token JWT.
    El campo 'id' (sub) es el identificador del usuario.
    """
    id: Optional[str] = None