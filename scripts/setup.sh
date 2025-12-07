#!/bin/bash
# ==============================================================================
# Script: setup.sh
# Description: Automatiza la configuracion inicial del proyecto para Linux (Debian).
# Author: El checon
# ==============================================================================

# Detener el script si un comando falla
set -e

# --- FASE 0: VERIFICACION INICIAL ---
echo "======================================================"
echo "VERIFICANDO ENTORNO"
echo "======================================================"

# Verificar que el script se ejecuta desde la raiz del proyecto
if [ ! -f "requirements.txt" ] || [ ! -d "app" ]; then
    echo "[ERROR] Este script debe ser ejecutado desde la raiz del proyecto." >&2
    echo "Por favor, navega a la carpeta raiz y ejecuta el script asi: ./scripts/setup.sh" >&2
    exit 1
fi

# Crear directorio de logs y redirigir toda la salida alli
mkdir -p logs
LOG_FILE="logs/setup.log"
exec &> >(tee -a "$LOG_FILE")

echo "======================================================"
echo "INICIANDO CONFIGURACION DEL ENTORNO DE DESARROLLO"
echo "======================================================"

# --- FASE 1: PREPARACION Y ENTORNO VIRTUAL ---
echo -e "\n[FASE 1/6] Preparando el entorno virtual..."

# 1. Verificar Python y venv
echo "Verificando instalacion de Python3 y venv..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 no esta instalado. Por favor, instalalo con 'sudo apt-get install python3'." >&2
    exit 1
fi

if ! python3 -c "import venv" &> /dev/null; then
    echo "El modulo venv de Python3 no esta instalado. Por favor, instalalo con 'sudo apt-get install python3-venv'." >&2
    exit 1
fi
echo "Python3 y venv encontrados."

# 2. Crear Entorno Virtual
if [ ! -d "../.venv" ]; then
    echo "Creando entorno virtual en '../.venv'..."
    python3 -m venv ../.venv
    echo "Entorno virtual creado."
else
    echo "El entorno virtual '../.venv' ya existe."
fi

# 3. Activar el Entorno Virtual
echo "Activando el entorno virtual..."
source ../.venv/bin/activate
echo "Entorno activado."

# 4. Instalar Dependencias
echo "Instalando dependencias desde 'requirements.txt'..."
pip install -r requirements.txt
echo "Dependencias instaladas correctamente."

# --- FASE 2: GENERACION DE CLAVE Y CONFIGURACION DEL .env ---
echo -e "\n[FASE 2/6] Configurando el archivo de entorno..."

# 1. Generar Clave
echo "Generando nueva clave de encriptacion..."
FERNET_KEY=$(python3 -m seed.gen_first_key)
echo "Clave generada."

# 2. Manejo del .env
if [ ! -f ".env" ]; then
    echo "Creando archivo '.env' desde '.env.example'..."
    cp ./.env.example ./.env
else
    echo "El archivo '.env' ya existe."
fi

# 3. Instruir al Usuario
echo "------------------------------------------------------------------"
echo "[ACCION REQUERIDA]"
echo "Se ha generado una nueva clave de encriptacion:"
echo -e "\nCLAVE: $FERNET_KEY"
echo -e "\nPor favor, abre el archivo '.env' y pega esta clave como valor para 'FERNET_KEY'."
echo "Ejemplo: FERNET_KEY='$FERNET_KEY'"
echo "------------------------------------------------------------------"
read -p "Presiona Enter cuando hayas guardado el archivo '.env' para continuar..."

# --- FASE 3: CREACION DE LA BASE DE DATOS INICIAL ---
echo -e "\n[FASE 3/6] Inicializando la base de datos..."
mkdir -p db
python3 -m seed.setup_data
echo "Base de datos inicializada correctamente."

# --- FASE 4: CREACION DE ARCHIVOS DE LOG ---
echo -e "\n[FASE 4/6] Creando archivos de log..."
mkdir -p logs
touch logs/app.log logs/errors.log logs/tasks.log
echo "Archivos de log creados."

# --- FASE 5: VERIFICACION Y PRUEBAS ---
echo -e "\n[FASE 5/6] Ejecutando pruebas unitarias..."
python3 -m pytest
echo "Todas las pruebas pasaron exitosamente."

# --- FASE 6: EJECUCION DE LA APLICACION ---
echo -e "\n[FASE 6/6] ¡Configuracion completada!"
echo "Todo esta listo para empezar a desarrollar."
echo "Para iniciar el servidor, puedes ejecutar el script 'start_server.sh' o el comando 'python3 -m app.main'."
echo "Servidor disponible en: http://127.0.0.1:5000"

# Desactivar entorno virtual al finalizar
deactivate
