# 📚 Task Manager API (FastAPI + MongoDB)

## Desarrollado por: [Franco Gerbino]

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248.svg)
![Docker](https://img.shields.io/badge/Docker-20.10+-blue)
![Pydantic](https://img.shields.io/badge/Pydantic-2.5+-green)

---

## 💡 Sobre el Proyecto

Este proyecto es una **API RESTful robusta y asíncrona** para la gestión de tareas, construida con **FastAPI** y **MongoDB**. Utiliza la arquitectura asíncrona de Python para manejar altas cargas de concurrencia y se apoya en un patrón de repositorio para separar la lógica de negocio de la capa de datos.

Este proyecto fue diseñado para demostrar el dominio de:

1.  **Backend Asíncrono:** Uso de `async`/`await` para operaciones de I/O bloqueantes (Motor).
2.  **Autenticación JWT:** Implementación de un sistema seguro de registro e inicio de sesión con tokens.
3.  **Dockerización:** Gestión y ejecución de la base de datos de forma aislada.
4.  **Patrón de Repositorio:** Gestión limpia y modular del código.

## ⚙️ Características Principales

| Módulo | Funcionalidad | Descripción Técnica |
|        :---        |      :---       |                               :---                             |
| **Autenticación** | Registro y Login | **JWT (JSON Web Tokens)** con hashing de contraseñas (Bcrypt). |
| **Usuarios** | Propiedad de Tareas | Cada tarea está asociada al ID del usuario que la creó, garantizando la seguridad por propietario. |
| **Tareas** | CRUD (Crear, Leer, Actualizar, Borrar) | Gestión completa del ciclo de vida de la tarea. |
| **Seguridad** | Dependencias de Seguridad | Rutas protegidas que requieren un Access Token válido para acceder. |

---

## 🚀 Puesta en Marcha (Instalación Local)

### Prerrequisitos

Asegúrate de tener instalado lo siguiente:

* **Python 3.10+** (Se recomienda usar un entorno virtual).
* **Docker Desktop** (Para levantar la base de datos MongoDB).

### 1. Clonar el Repositorio

Abre tu terminal y navega hasta donde quieras guardar el proyecto:

```bash
git clone [https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories](https://docs.github.com/es/repositories/creating-and-managing-repositories/quickstart-for-repositories)
cd nombre-del-repo-local