# 📚 Task Manager API

Una **API RESTful asíncrona y completamente funcional** para la gestión de tareas, construida con **FastAPI** y **MongoDB**. 

![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248.svg)
![Docker](https://img.shields.io/badge/Docker-Containerizado-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📖 Tabla de Contenidos

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Endpoints](#endpoints)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías](#tecnologías)

---

## ✨ Características

### 🔐 Autenticación y Seguridad
- ✅ **Registro de usuarios** con validación de email
- ✅ **Login con JWT tokens** (JSON Web Tokens)
- ✅ **Hashing de contraseñas** con Argon2 (más seguro que bcrypt)
- ✅ **Protección de rutas** con Bearer token authentication
- ✅ **Tokens con expiración** (configurable)

### 👤 Gestión de Usuarios
- ✅ Obtener perfil del usuario autenticado
- ✅ Información de usuario en base de datos segura
- ✅ Validación de email único

### 📋 CRUD Completo de Tareas
- ✅ **Crear** tareas con título, descripción y fecha de vencimiento
- ✅ **Leer** todas las tareas del usuario
- ✅ **Leer** una tarea específica por ID
- ✅ **Actualizar** tareas (título, descripción, estado de completación)
- ✅ **Eliminar** tareas
- ✅ Tareas asociadas al usuario propietario (seguridad)

### 🏗️ Arquitectura
- ✅ **Patrón de Repositorio** para separación de concerns
- ✅ **Operaciones asíncronas** con async/await
- ✅ **Validación de datos** con Pydantic v2
- ✅ **Documentación automática** con Swagger UI y ReDoc

---

## 🔧 Requisitos Previos

Asegúrate de tener instalado:

- **Python 3.10+** (se recomienda 3.12+)
- **Docker y Docker Compose** (para MongoDB)
- **Git** (para clonar el repositorio)
- **pip** o **pipenv** (gestor de paquetes Python)

### Verificar instalación:
```bash
python --version
docker --version
git --version
```

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/francogerbino87-creator/task-manager-api.git
cd task-manager-api
```

### 2. Crear y activar entorno virtual (opcional pero recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install fastapi uvicorn motor pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] argon2-cffi email-validator python-multipart requests
```

O si tienes `Pipfile`:
```bash
pipenv install
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=task_manager_db
MONGODB_USERS_COLLECTION=users
MONGODB_TASKS_COLLECTION=tasks

# JWT Configuration
SECRET_KEY=tu_clave_secreta_super_segura_de_desarrollo
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Application
PROJECT_NAME=Task Manager API
API_VERSION=v1
```

### 5. Iniciar MongoDB con Docker

```bash
docker run -d --name task-manager-mongo -p 27017:27017 mongo:latest
```

---

## 🚀 Uso

### Iniciar el servidor

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El servidor estará disponible en: **http://localhost:8000**

### Acceder a la documentación

- **Swagger UI (Recomendado)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Desde Swagger UI puedes probar todos los endpoints directamente.

---

## 📡 Endpoints

### 🔐 Autenticación (`/api/v1/auth`)

#### Registrar usuario
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

Response (201):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Login
```
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=usuario@example.com&password=SecurePass123

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 👤 Usuarios (`/api/v1/users`)

#### Obtener perfil autenticado
```
GET /api/v1/users/me
Authorization: Bearer {token}

Response (200):
{
  "id": "507f1f77bcf86cd799439011",
  "email": "usuario@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

### 📋 Tareas (`/api/v1/tasks`)

#### Crear tarea
```
POST /api/v1/tasks/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Completar proyecto",
  "description": "Terminar el Task Manager API",
  "due_date": "2026-02-15T10:00:00"
}

Response (201): Task created
```

#### Listar tareas del usuario
```
GET /api/v1/tasks/
Authorization: Bearer {token}

Response (200):
{
  "tasks": [...],
  "total": 1,
  "page": 1,
  "size": 10
}
```

#### Obtener tarea por ID
```
GET /api/v1/tasks/{task_id}
Authorization: Bearer {token}

Response (200): Task object
```

#### Actualizar tarea
```
PUT /api/v1/tasks/{task_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Proyecto completado",
  "completed": true
}

Response (200): Updated task object
```

#### Eliminar tarea
```
DELETE /api/v1/tasks/{task_id}
Authorization: Bearer {token}

Response (204): No Content
```

---

## 📁 Estructura del Proyecto

```
task-manager-api/
├── app/
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── api/
│   ├── core/
│   │   ├── security.py         # JWT y hashing
│   │   ├── dependencies.py     # DI
│   │   └── auth_dependency.py
├── config/
│   ├── settings.py             # Configuración
│   └── database.py             # MongoDB connection
├── repositories/
│   ├── user_repository.py
│   └── task_repository.py
├── routes/
│   ├── auth_routes.py
│   ├── task_routes.py
│   └── user_routes.py
├── schemas/
│   ├── user_schema.py
│   ├── task_schema.py
│   └── token_schema.py
├── services/
│   └── auth_service.py
├── .env
├── .gitignore
├── README.md
├── final_test.py
└── requirements.txt
```

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Propósito |
|-----------|-----------|
| **FastAPI** | Framework web asíncrono |
| **Python** | Lenguaje de programación |
| **MongoDB** | Base de datos NoSQL |
| **Motor** | Driver async para MongoDB |
| **Pydantic** | Validación de datos |
| **JWT** | Autenticación segura |
| **Argon2** | Hashing de contraseñas |
| **Docker** | Containerización |

---

## 🧪 Testing

Ejecutar el script de pruebas:

```bash
python final_test.py
```

Resultado esperado:
```
✅ TEST 1: REGISTRO - 201 OK
✅ TEST 2: LOGIN - 200 OK
✅ TEST 3: OBTENER PERFIL - 200 OK
✅ TEST 4: CREAR TAREA - 201 OK
✅ TEST 5: LISTAR TAREAS - 200 OK
✅ TEST 6: OBTENER TAREA POR ID - 200 OK
✅ TEST 7: ACTUALIZAR TAREA - 200 OK
✅ TEST 8: ELIMINAR TAREA - 204 OK
```

---

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con Argon2
- ✅ JWT tokens con expiración
- ✅ Protección de rutas con autenticación
- ✅ Validación de email
- ✅ Control de acceso basado en propietario

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 👨‍💻 Autor

**Franco Gerbino**
- GitHub: [@francogerbino87-creator](https://github.com/francogerbino87-creator)

---

## 🎉 Estado del Proyecto

✅ **Completamente funcional y testeado**

Todos los endpoints funcionan correctamente y han sido validados con pruebas de integración completas.

**Última actualización:** 2 de Febrero, 2026
