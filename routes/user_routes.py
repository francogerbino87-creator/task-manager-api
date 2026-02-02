from fastapi import APIRouter, Depends, status

from schemas.user_schema import UserResponse, UserInDB # Importamos UserInDB para la dependencia
from app.core.auth_dependency import get_current_user # La nueva dependencia

# --- Configuración de Router ---
router = APIRouter(prefix="/users", tags=["Usuarios"])

# --- Endpoint de Perfil Protegido ---
@router.get("/me", response_model=UserResponse)
async def read_users_me(
    # La clave CRÍTICA: La dependencia get_current_user se encarga de:
    # 1. Extraer el token del encabezado Authorization.
    # 2. Decodificarlo y validar la expiración.
    # 3. Buscar el usuario en la base de datos.
    # 4. Si todo es exitoso, inyecta el objeto UserInDB.
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actualmente autenticado (ruta protegida).
    """
    # Devolvemos el usuario (limitado a UserResponse para ocultar el hash de la contraseña)
    return current_user