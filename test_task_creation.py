import requests
import json
import sys
from typing import Optional

# !!! IMPORTANTE: REEMPLAZA ESTE VALOR CON EL TOKEN QUE OBTUVISTE AL HACER LOGIN !!!
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTE1MTAwNzE3ZTk5ZmRmMjk0MWYzNzUiLCJleHAiOjE3NjI5OTI0OTgsImlhdCI6MTc2Mjk4ODg5OH0.3-yuGI2WPk6nj1L3p-lX6fQmpH73vmz6A6ZIvs5QPn8" 

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
TASKS_URL = f"{BASE_URL}/tasks"

# Cabeceras de la solicitud, incluyendo la autenticación Bearer
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Datos iniciales para la creación
CREATE_DATA = {
    "title": "Tarea de Prueba para CRUD",
    "description": "Se debe actualizar y luego eliminar.",
    "status": "pending"
}

# Datos para la actualización
UPDATE_DATA = {
    "title": "Tarea ACTULIZADA y COMPLETA",
    "status": "completed",
    "completed": True # Asumiendo que tu modelo usa 'completed' o 'status'
}

def check_token_and_exit():
    """Verifica si el token es el placeholder."""
    if ACCESS_TOKEN == "PEGA_TU_TOKEN_LARGO_AQUI":
        print("\nERROR: Debes reemplazar 'PEGA_TU_TOKEN_LARGO_AQUI' con el token real de tu login.")
        sys.exit(1)

def create_task() -> Optional[str]:
    """Crea una nueva tarea y retorna su ID."""
    print(f"\n--- 1. POST /tasks (CREAR) ---")
    
    try:
        response = requests.post(TASKS_URL, headers=headers, data=json.dumps(CREATE_DATA))
        
        print(f"Código de respuesta: {response.status_code}")
        
        if response.status_code == 201:
            task_response = response.json()
            created_task_id = task_response.get('_id')
            
            if created_task_id:
                print(f"✅ ÉXITO: Tarea creada con ID: {created_task_id}")
            return created_task_id
        
        elif response.status_code == 401:
            print("❌ FALLO: CÓDIGO 401 (No Autorizado). Token inválido.")
        else:
            print(f"❌ FALLO: Código inesperado. Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR de conexión: Uvicorn no está corriendo. Detalles: {e}")
    return None

def update_task(task_id: str) -> bool:
    """Actualiza una tarea existente."""
    url = f"{TASKS_URL}/{task_id}"
    print(f"\n--- 2. PUT /tasks/{task_id} (ACTUALIZAR) ---")
    
    try:
        response = requests.put(url, headers=headers, data=json.dumps(UPDATE_DATA))
        
        print(f"Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ÉXITO: Tarea actualizada correctamente.")
            updated_task = response.json()
            # Verificamos si los datos se aplicaron
            if updated_task.get('status') == UPDATE_DATA['status']:
                 print(f"   Datos verificados: Status es '{updated_task.get('status')}'")
            return True
        elif response.status_code == 404:
             print("❌ FALLO: CÓDIGO 404. Tarea no encontrada o no pertenece al usuario.")
        elif response.status_code == 401:
            print("❌ FALLO: CÓDIGO 401. Token inválido.")
        else:
            print(f"❌ FALLO: Código inesperado. Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR de conexión: {e}")
    return False

def delete_task(task_id: str) -> bool:
    """Elimina una tarea."""
    url = f"{TASKS_URL}/{task_id}"
    print(f"\n--- 3. DELETE /tasks/{task_id} (ELIMINAR) ---")
    
    try:
        response = requests.delete(url, headers=headers)
        
        print(f"Código de respuesta: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ ÉXITO: Tarea eliminada correctamente (204 No Content).")
            # Opcionalmente, puedes probar a leer la tarea para confirmar la eliminación
            return True
        elif response.status_code == 404:
            print("❌ FALLO: CÓDIGO 404. Tarea no encontrada o no pertenece al usuario.")
        else:
            print(f"❌ FALLO: Código inesperado. Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR de conexión: {e}")
    return False

def run_full_crud_test():
    """Ejecuta la secuencia completa de pruebas CRUD."""
    check_token_and_exit()
    
    task_id = create_task()
    
    if task_id:
        update_success = update_task(task_id)
        
        if update_success:
            delete_task(task_id)
            
    print("\n--- PRUEBA CRUD FINALIZADA ---")

if __name__ == "__main__":
    run_full_crud_test()

### 🏃 Pasos para la Prueba Final

# 1.  **Crea el archivo:** Guarda el código de arriba como **`test_task_crud.py`**.
# 2.  **Pega el token:** Reemplaza el `ACCESS_TOKEN` con tu token de login actual.
# 3.  **Inicia Uvicorn:** Asegúrate de que `uvicorn app.main:app --reload` esté corriendo en una terminal.
# 4.  **Ejecuta el script:** `python test_task_crud.py`

# Si obtienes `201`, `200` y `204` en orden, ¡la API está 100% validada!