#!/bin/bash
# ==============================================================================
# Script: start_server.sh
# Description: Inicia el servidor de desarrollo de Flask en Linux (Debian).
# Author: El checon
# ==============================================================================

# Detener el script si un comando falla
set -e

# --- VERIFICACION INICIAL ---
# Verificar que el script se ejecuta desde la raiz del proyecto
if [ ! -f "requirements.txt" ] || [ ! -d "app" ]; then
    echo "[ERROR] Este script debe ser ejecutado desde la raiz del proyecto." >&2
    echo "Por favor, navega a la carpeta raiz y ejecuta el script asi: ./scripts/start_server.sh" >&2
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p logs
LOG_FILE="logs/start_server.log"

# --- INICIO DEL SERVIDOR ---
echo "================================================"
echo "INICIANDO SERVIDOR DE DESARROLLO"
echo "================================================"

# Redirigir stdout/stderr al log y a la consola
exec &> >(tee -a "$LOG_FILE")

# 1. Verificar Entorno Virtual
echo -e "\nVerificando la existencia del entorno virtual..."
if [ ! -f "../.venv/bin/activate" ]; then
    echo "[ERROR] El entorno virtual no se encuentra. Por favor, ejecuta el script 'setup.sh' primero." >&2
    exit 1
fi
echo "Entorno virtual encontrado."

# 2. Activar el Entorno Virtual
echo "Activando el entorno virtual..."
source ../.venv/bin/activate
echo "Entorno activado."

# 3. Iniciar la Aplicacion Flask
echo -e "\nIniciando el servidor Flask..."
echo "Presiona CTRL+C para detener el servidor."
echo "El servidor estará disponible en: http://127.0.0.1:5000"

python3 -m app.main

# Nota: El script terminará aquí cuando el proceso de python termine.
# La desactivación del entorno virtual no es estrictamente necesaria
# ya que el script finaliza, pero es una buena práctica.
deactivate
echo -e "\nEl servidor se ha detenido."
