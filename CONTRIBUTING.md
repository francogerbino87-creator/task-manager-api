# Contributing

Gracias por interesarte en contribuir a Task Manager API. Esta guía explica cómo configurar el entorno, el flujo de trabajo recomendado y buenas tareas para comenzar.

## Antes de empezar
- Lee el `README.md` para entender la API y cómo levantar el proyecto.
- Abre un issue antes de trabajar en cambios significativos para discutir la implementación.

## Configuración rápida
1. Clona el repositorio:

```bash
git clone https://github.com/francogerbino87-creator/task-manager-api.git
cd task-manager-api
```

2. Crea y activa un entorno virtual (recomendado):

Windows:
```powershell
python -m venv venv
venv\\Scripts\\activate
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt || pip install fastapi uvicorn motor pydantic pydantic-settings python-jose[cryptography] argon2-cffi email-validator python-multipart requests
```

4. Levanta MongoDB (recomendado con Docker) y exporta variables si usas `.env`.

5. Ejecuta tests:

```bash
python final_test.py
```

## Flujo de trabajo
- Crea una rama por cambio: `git checkout -b feat/descripcion-corta`.
- Mantén commits claros y atómicos. Sigue Conventional Commits cuando sea posible.
- Abre un Pull Request (PR) contra `main` cuando esté listo. Incluye descripción, cómo probar y screenshots si aplica.

## Estilo de código
- Mantén la misma estructura y estilo del repositorio.
- Usa async/await donde correspondan (la base del proyecto es asíncrona).
- Formatea con `black` (si está disponible) y ejecuta linters si los añades.

## Tests
- Añade pruebas para funcionalidades nuevas o corrección de bugs.
- Si agregas endpoints, incluye tests de integración similares a `final_test.py`.

## Buenas prácticas para PRs de trainees
- Describe el objetivo del cambio y los pasos para probarlo.
- Añade comentarios en el código donde algo no sea trivial.
- Si necesitas ayuda, etiqueta al mantenedor en el PR o deja un comentario en el issue asociado.

## Recursos de aprendizaje
- Revisa `app/main.py`, `services/auth_service.py`, `repositories/` y `schemas/` para entender la arquitectura.
- Si eres nuevo en FastAPI o Motor, la documentación oficial es muy útil:
  - https://fastapi.tiangolo.com/
  - https://motor.readthedocs.io/

Gracias por contribuir — cada aporte mejora el proyecto y ayuda a otros a aprender.
