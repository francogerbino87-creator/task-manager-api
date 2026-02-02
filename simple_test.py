#!/usr/bin/env python
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("Intentando conectar al servidor...")
time.sleep(1)

try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
