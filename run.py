import subprocess
import sys
import os
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- 1. Determinación y Configuración de la Ruta Raíz ---
project_root = os.path.dirname(os.path.abspath(__file__))
logging.info(f"Ruta raíz del proyecto: {project_root}")

# AÑADIR LA RUTA AL sys.path del proceso actual (para el proceso principal)
# Esto es CRUCIAL para que Python encuentre 'app' como paquete de nivel superior
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    logging.info("Ruta raíz insertada en sys.path.")

# --- 2. FIX CRUCIAL: Configurar PYTHONPATH para Subprocesos (para el reloader) ---
# Exportar PYTHONPATH para que los procesos hijos (como el reloader de Uvicorn) 
# puedan encontrar el paquete 'app'.
current_env = os.environ.copy()
# Añadimos la ruta raíz al PYTHONPATH. os.pathsep es el separador correcto para el OS.
# Es importante preservar el valor original si existe.
current_env['PYTHONPATH'] = project_root + os.pathsep + current_env.get('PYTHONPATH', '')

logging.info(f"PYTHONPATH configurado: {current_env['PYTHONPATH']}")


# 3. Comando Uvicorn para ejecutar la aplicación
# Usamos sys.executable para garantizar que usamos el intérprete de nuestro entorno virtual.
command = [
    sys.executable,  
    "-m", "uvicorn", 
    "app.main:app", 
    "--reload"
]

logging.info("Iniciando Uvicorn...")

# 4. Ejecuta Uvicorn
try:
    print("Comando de Uvicorn:", " ".join(command[2:]))
    # Pasamos el entorno modificado al subproceso
    subprocess.run(command, env=current_env) 
except KeyboardInterrupt:
    logging.info("\nUvicorn detenido por el usuario.")
except Exception as e:
    logging.error(f"Fallo al iniciar Uvicorn: {e}")