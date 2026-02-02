# Feat: Pagination & Filters (skeleton)

Este directorio contiene un esqueleto para implementar paginación y filtros en `GET /tasks`.

Objetivos:
- Añadir query params `page`, `page_size`, `completed`, `due_before` a `GET /tasks`.
- Actualizar repositorio para aceptar esos parámetros y devolver metadata (`total`, `page`, `page_size`).

Archivos sugeridos a modificar:
- `routes/task_routes.py`
- `repositories/task_repository.py`
- `schemas/task_schema.py`

Ejemplo de uso del repository (pseudo-código):

```python
from datetime import datetime
from typing import Optional

async def get_all_tasks(db, owner_id: str, page: int = 1, page_size: int = 20, completed: Optional[bool] = None, due_before: Optional[str] = None):
    skip = (page - 1) * page_size
    query = {"owner_id": owner_id}
    if completed is not None:
        query["completed"] = completed
    if due_before:
        query["due_date"] = {"$lt": datetime.fromisoformat(due_before)}
    cursor = db["tasks"].find(query).skip(skip).limit(page_size)
    items = await cursor.to_list(length=page_size)
    total = await db["tasks"].count_documents(query)
    return {"items": items, "total": total, "page": page, "page_size": page_size}
```

Pruebas recomendadas:
- Añadir tests que creen varias tareas y verifiquen que la paginación y filtros funcionan.
