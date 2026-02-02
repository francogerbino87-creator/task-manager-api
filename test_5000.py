#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random
import string
import json
import time

# Configuración
BASE_URL = "http://127.0.0.1:5000/api/v1"

def generate_random_email():
    return f"user_{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"

def test_api():
    print("\n" + "="*60)
    print("PRUEBAS DE INTEGRACION DEL TASK MANAGER API")
    print("="*60)
    
    # Variables para almacenar token e IDs
    token = None
    task_id = None
    email = generate_random_email()
    password = "SecurePass123"
    
    # ===== PRUEBA 1: REGISTRO =====
    print("\n[1] PROBANDO REGISTRO DE USUARIO")
    print(f"    Email: {email}")
    print(f"    Password: {password}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        
        if response.status_code == 201:
            print("    [OK] Registro exitoso (201)")
            data = response.json()
            token = data.get("access_token")
            print(f"    Token obtenido: {token[:20]}...")
        else:
            print(f"    [FALLO] Status {response.status_code}")
            print(f"    Response: {response.text}")
            return
    except Exception as e:
        print(f"    [ERROR] {str(e)}")
        return
    
    # ===== PRUEBA 2: LOGIN =====
    print("\n[2] PROBANDO LOGIN")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": email,
            "password": password
        })
        
        if response.status_code == 200:
            print("    [OK] Login exitoso (200)")
            data = response.json()
            token = data.get("access_token")
            print(f"    Token obtenido: {token[:20]}...")
        else:
            print(f"    [FALLO] Status {response.status_code}")
            print(f"    Response: {response.text}")
            return
    except Exception as e:
        print(f"    [ERROR] {str(e)}")
        return
    
    # Preparar headers con token
    headers = {"Authorization": f"Bearer {token}"}
    
    # ===== PRUEBA 3: OBTENER PERFIL =====
    print("\n[3] PROBANDO OBTENER PERFIL DE USUARIO")
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            print("    [OK] Perfil obtenido (200)")
            user = response.json()
            print(f"    Email: {user.get('email')}")
            print(f"    Nombre: {user.get('full_name')}")
        else:
            print(f"    [FALLO] Status {response.status_code}")
            print(f"    Response: {response.text}")
    except Exception as e:
        print(f"    [ERROR] {str(e)}")
    
    # ===== PRUEBA 4: CREAR TAREA =====
    print("\n[4] PROBANDO CREAR TAREA")
    
    try:
        task_data = {
            "title": "Tarea de prueba",
            "description": "Esta es una tarea de prueba del sistema",
            "due_date": "2026-02-15T10:00:00"
        }
        
        response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
        
        if response.status_code == 201:
            print("    [OK] Tarea creada (201)")
            task = response.json()
            task_id = task.get("id")
            print(f"    Task ID: {task_id}")
            print(f"    Titulo: {task.get('title')}")
        else:
            print(f"    [FALLO] Status {response.status_code}")
            print(f"    Response: {response.text}")
    except Exception as e:
        print(f"    [ERROR] {str(e)}")
    
    # ===== PRUEBA 5: LISTAR TAREAS =====
    print("\n[5] PROBANDO LISTAR TAREAS")
    
    try:
        response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
        
        if response.status_code == 200:
            print("    [OK] Tareas obtenidas (200)")
            data = response.json()
            tasks = data.get("tasks", [])
            print(f"    Total de tareas: {len(tasks)}")
            for task in tasks:
                print(f"      - {task.get('title')} (ID: {task.get('id')})")
        else:
            print(f"    [FALLO] Status {response.status_code}")
            print(f"    Response: {response.text}")
    except Exception as e:
        print(f"    [ERROR] {str(e)}")
    
    # ===== PRUEBA 6: OBTENER TAREA POR ID =====
    if task_id:
        print("\n[6] PROBANDO OBTENER TAREA POR ID")
        
        try:
            response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
            
            if response.status_code == 200:
                print("    [OK] Tarea obtenida (200)")
                task = response.json()
                print(f"    Titulo: {task.get('title')}")
                print(f"    Descripcion: {task.get('description')}")
                print(f"    Completada: {task.get('completed')}")
            else:
                print(f"    [FALLO] Status {response.status_code}")
                print(f"    Response: {response.text}")
        except Exception as e:
            print(f"    [ERROR] {str(e)}")
        
        # ===== PRUEBA 7: ACTUALIZAR TAREA =====
        print("\n[7] PROBANDO ACTUALIZAR TAREA")
        
        try:
            update_data = {
                "title": "Tarea actualizada",
                "completed": True
            }
            
            response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data, headers=headers)
            
            if response.status_code == 200:
                print("    [OK] Tarea actualizada (200)")
                task = response.json()
                print(f"    Nuevo titulo: {task.get('title')}")
                print(f"    Completada: {task.get('completed')}")
            else:
                print(f"    [FALLO] Status {response.status_code}")
                print(f"    Response: {response.text}")
        except Exception as e:
            print(f"    [ERROR] {str(e)}")
        
        # ===== PRUEBA 8: ELIMINAR TAREA =====
        print("\n[8] PROBANDO ELIMINAR TAREA")
        
        try:
            response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
            
            if response.status_code == 204:
                print("    [OK] Tarea eliminada (204)")
            else:
                print(f"    [FALLO] Status {response.status_code}")
                print(f"    Response: {response.text}")
        except Exception as e:
            print(f"    [ERROR] {str(e)}")
    
    # ===== RESUMEN =====
    print("\n" + "="*60)
    print("PRUEBAS COMPLETADAS")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_api()
