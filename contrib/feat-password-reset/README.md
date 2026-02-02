# Feat: Password Reset (skeleton)

Este directorio contiene un esqueleto para implementar la funcionalidad de solicitud de reseteo de contraseña.

Objetivos:
- Añadir endpoint `POST /auth/request-password-reset` que genere un token seguro y lo guarde en la colección `users` con expiración.
- Mantener privacidad: siempre responder 200 aunque el email no exista.

Campos sugeridos en la colección `users`:
- `password_reset_token` (str)
- `password_reset_expires` (datetime)

Ejemplo de función para generar y guardar el token (pseudo-código):

```python
import secrets
from datetime import datetime, timedelta

async def request_password_reset(user_repo, email: str):
    user = await user_repo.get_by_email(email)
    if not user:
        return
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    await user_repo.set_password_reset_token(user.id, token, expires)
    # opcional: enviar email real desde infra externa
```

Sugerencia de archivos a editar:
- `routes/auth_routes.py` (nueva ruta)
- `repositories/user_repository.py` (guardar token/expiry)
- `services/auth_service.py` (lógica si quieres centralizar)

Pruebas recomendadas:
- Verificar que cuando el email existe, el token y la expiración se guardan.
- Verificar que la API responde 200 también cuando el email no existe.
