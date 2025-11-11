from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    """
    Excepción personalizada para manejar el error 404 (Not Found).
    
    Se utiliza cuando un recurso (como una tarea o un usuario) 
    no es encontrado en la base de datos o no pertenece al usuario actual.
    """
    def __init__(self, detail: str = "Recurso no encontrado o no autorizado."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

# Opcional: Puedes agregar otras excepciones comunes aquí si las necesitas
# class ConflictException(HTTPException):
#     def __init__(self, detail: str = "El recurso ya existe."):
#         super().__init__(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=detail
#         )