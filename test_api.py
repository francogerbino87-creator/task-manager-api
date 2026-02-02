import requests
import random
import string

# Configuración
BASE_URL = "http://127.0.0.1:8000/api/v1"

def generate_random_email():
    return f"user_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"

def run_test():
    print("🚀 Iniciando pruebas de integración API...\n")
    
    # 1. Datos para registro
    email = generate_random_email()
    password = "password123"
    print(f"1. Intentando registrar usuario: {email}")
    
    # 2. REGISTRO
    reg_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    
    if reg_response.status_code == 201:
        print("   ✅ Registro exitoso (201 Created)")
    else:
        print(f"   ❌ Fallo en registro: {reg_response.text}")
        return

    # 3. LOGIN
    print(f"2. Intentando iniciar sesión...")
    login_response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": email, # OAuth2 espera 'username' aunque sea el email
        "password": password
    })
    
    token = None
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print("   ✅ Login exitoso. Token obtenido.")
        print(f"   🔑 Token: {token[:15]}...") 
    else:
        print(f"   ❌ Fallo en login: {login_response.text}")
        return

    # 4. PRUEBA DE RUTA PROTEGIDA (Perfil de Usuario)
    print(f"3. Accediendo a ruta protegida (/users/me)...")
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if me_response.status_code == 200:
        user_data = me_response.json()
        print(f"   ✅ Acceso autorizado exitoso.")
        print(f"   👤 Usuario recuperado: {user_data['email']}")
    else:
        print(f"   ❌ Fallo en ruta protegida: {me_response.status_code} - {me_response.text}")

    # 5. PRUEBA DE TAREAS (Crear Tarea)
    print(f"4. Creando una tarea de prueba...")
    task_data = {"title": "Tarea de prueba script", "description": "Creada automáticamente"}
    task_response = requests.post(f"{BASE_URL}/tasks/", headers=headers, json=task_data)
    
    if task_response.status_code == 201:
        print("   ✅ Tarea creada exitosamente.")
    else:
        print(f"   ❌ Fallo al crear tarea: {task_response.text}")

if __name__ == "__main__":
    # Asegúrate de tener 'requests' instalado: pip install requests
    try:
        import requests
        run_test()
    except ImportError:
        print("Error: La librería 'requests' no está instalada.")
        print("Ejecuta: pip install requests")