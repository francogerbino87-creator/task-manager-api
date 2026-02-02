# Good First Issues

Estas son ideas de trabajo pensadas para trainees o nuevos contribuidores. Cada tarea incluye descripción, criterios de aceptación y sugerencias de archivos a modificar.

---

## 1) Paginación y filtros en `GET /tasks`

**Descripción:** Añadir soporte de paginación (p. ej. `page`, `page_size`) y filtros básicos (`completed`, `due_before`) al endpoint que lista tareas.

**Por qué:** Mejora la usabilidad y prepara la API para conjuntos de datos mayores.

**Criterios de aceptación:**
- El endpoint `GET /tasks` acepta query params `page` (int, default 1), `page_size` (int, default 20).
- Soporta `completed=true|false` para filtrar por estado.
- Soporta `due_before=YYYY-MM-DD` para devolver solo tareas con `due_date` anterior.
- Los tests actualizados cubren paginación y filtros.

**Sugerencia de archivos a editar:**
- `routes/task_routes.py`
- `repositories/task_repository.py`
- `schemas/task_schema.py` (si es necesario añadir respuesta con `total`/`page` info)
- Añadir tests en `final_test.py` o nuevo archivo de tests.

**Dificultad:** Fácil–Media

---

## 2) Endpoint para solicitar reset de contraseña (esqueleto)

**Descripción:** Implementar un endpoint inicial para solicitar un reseteo de contraseña. No es necesario integrar email real; basta con generar un token de reset y guardarlo en DB con expiración.

**Por qué:** Es una funcionalidad real-world que enseña manejo de tokens temporales y modificaciones de usuario.

**Criterios de aceptación:**
- `POST /auth/request-password-reset` recibe `{ "email": "user@example.com" }` y responde 200 incluso si el email no existe (no revelar usuarios).
- Si el usuario existe, guarda un `password_reset_token` y `password_reset_expires` en la colección `users`.
- Añadir test que verifica que el token y fecha se guardan cuando el usuario existe.

**Sugerencia de archivos a editar:**
- `routes/auth_routes.py` (nueva ruta)
- `repositories/user_repository.py` (guardar token/expiry)
- `services/auth_service.py` (lógica de token)
- Añadir tests en `final_test.py` o nuevo archivo de tests.

**Dificultad:** Fácil

---

Si quieres, puedo crear ramas y PRs por estas tareas, o generar plantillas de issues listas para pegar en GitHub.
