#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_registration():
    print("\n=== TEST 1: REGISTRO ===")
    email = f"test_{random.randint(1000, 9999)}@example.com"
    password = "TestPass123"
    
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("OK - Registro exitoso")
        return response.json().get("access_token"), email, password
    else:
        print(f"FALLO - {response.text}")
        return None, email, password

def test_login(email, password):
    print("\n=== TEST 2: LOGIN ===")
    
    response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": email,
        "password": password
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("OK - Login exitoso")
        return response.json().get("access_token")
    else:
        print(f"FALLO - {response.text}")
        return None

def test_get_profile(token):
    print("\n=== TEST 3: OBTENER PERFIL ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("OK - Perfil obtenido")
        print(f"Email: {response.json().get('email')}")
        return True
    else:
        print(f"FALLO - {response.text}")
        return False

def test_create_task(token):
    print("\n=== TEST 4: CREAR TAREA ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Mi primera tarea",
        "description": "Tarea de prueba",
        "due_date": None
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("OK - Tarea creada")
        return response.json().get("id")
    else:
        print(f"FALLO - {response.text}")
        return None

def test_list_tasks(token):
    print("\n=== TEST 5: LISTAR TAREAS ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("OK - Tareas obtenidas")
        data = response.json()
        print(f"Total tareas: {len(data.get('tasks', []))}")
        return True
    else:
        print(f"FALLO - {response.text}")
        return False

def test_get_task(token, task_id):
    print("\n=== TEST 6: OBTENER TAREA POR ID ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("OK - Tarea obtenida")
        return True
    else:
        print(f"FALLO - {response.text}")
        return False

def test_update_task(token, task_id):
    print("\n=== TEST 7: ACTUALIZAR TAREA ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "title": "Tarea actualizada",
        "completed": True
    }
    
    response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("OK - Tarea actualizada")
        return True
    else:
        print(f"FALLO - {response.text}")
        return False

def test_delete_task(token, task_id):
    print("\n=== TEST 8: ELIMINAR TAREA ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("OK - Tarea eliminada")
        return True
    else:
        print(f"FALLO - {response.text}")
        return False

if __name__ == "__main__":
    print("INICIANDO PRUEBAS DEL TASK MANAGER API")
    print("=" * 50)
    
    # Test 1: Registro
    token, email, password = test_registration()
    
    if not token:
        print("\nNo se pudo registrar, intentando login...")
        token = test_login(email, password)
    
    if not token:
        print("\nNo se pudo obtener token. Deteniendo pruebas.")
        exit(1)
    
    # Test 3: Obtener perfil
    test_get_profile(token)
    
    # Test 4: Crear tarea
    task_id = test_create_task(token)
    
    # Test 5: Listar tareas
    test_list_tasks(token)
    
    if task_id:
        # Test 6: Obtener tarea por ID
        test_get_task(token, task_id)
        
        # Test 7: Actualizar tarea
        test_update_task(token, task_id)
        
        # Test 8: Eliminar tarea
        test_delete_task(token, task_id)
    
    print("\n" + "=" * 50)
    print("PRUEBAS COMPLETADAS")
    print("=" * 50)
