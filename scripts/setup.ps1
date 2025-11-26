# ==============================================================================
# Script: setup.ps1
# Description: Automatiza la configuracion inicial del proyecto para Windows.
# Author: El checon
# ==============================================================================

# Iniciar transcripcion para logging
$LogFile = "setup.log"
Start-Transcript -Path $LogFile -Append

# Verificar que el script se ejecuta desde la raiz del proyecto
if (-not (Test-Path "requirements.txt") -or -not (Test-Path "app")) {
    Write-Host "[ERROR] Este script debe ser ejecutado desde la raiz del proyecto." -ForegroundColor Red
    Write-Host "Por favor, navega a la carpeta raiz y ejecuta el script asi: .\scripts\setup.ps1" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

try {
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "INICIANDO CONFIGURACION DEL ENTORNO DE DESARROLLO" -ForegroundColor Cyan
    Write-Host "======================================================"

    # --- FASE 1: PREPARACION Y ENTORNO VIRTUAL ---
    Write-Host "`n[FASE 1/5] Preparando el entorno virtual..." -ForegroundColor Yellow

    # 1. Verificar Python
    Write-Host "Verificando instalacion de Python..."
    $pythonExists = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonExists) {
        throw "Python no esta instalado o no esta en el PATH. Por favor, instalalo y vuelve a ejecutar el script."
    }
    Write-Host "Python encontrado." -ForegroundColor Green

    # 2. Crear Entorno Virtual
    if (-not (Test-Path "..\.venv")) {
        Write-Host "Creando entorno virtual en '..\.venv'..."
        python -m venv ..\.venv
        Write-Host "Entorno virtual creado." -ForegroundColor Green
    } else {
        Write-Host "El entorno virtual '..\.venv' ya existe." -ForegroundColor Green
    }

    # 3. Activar el Entorno Virtual (para este script)
    Write-Host "Activando el entorno virtual..."
    . ..\.venv\Scripts\Activate.ps1
    Write-Host "Entorno activado." -ForegroundColor Green

    # 4. Instalar Dependencias
    Write-Host "Instalando dependencias desde 'requirements.txt'..."
    pip install -r requirements.txt
    Write-Host "Dependencias instaladas correctamente." -ForegroundColor Green

    # --- FASE 2: GENERACION DE CLAVE Y CONFIGURACION DEL .env ---
    Write-Host "`n[FASE 2/5] Configurando el archivo de entorno..." -ForegroundColor Yellow

    # 1. Generar Clave
    Write-Host "Generando nueva clave de encriptacion..."
    $fernetKey = python -m seed.gen_first_key
    Write-Host "Clave generada." -ForegroundColor Green

    # 2. Manejo del .env
    if (-not (Test-Path ".env")) {
        Write-Host "Creando archivo '.env' desde '.env.example'..."
        Copy-Item -Path ".\.env.example" -Destination ".\.env"
    } else {
        Write-Host "El archivo '.env' ya existe."
    }

    # 3. Instruir al Usuario
    Write-Host "------------------------------------------------------------------" -ForegroundColor Magenta
    Write-Host "[ACCION REQUERIDA]" -ForegroundColor Magenta
    Write-Host "Se ha generado una nueva clave de encriptacion:"
    Write-Host "`nCLAVE: $fernetKey" -ForegroundColor White
    Write-Host "`nPor favor, abre el archivo '.env' y pega esta clave como valor para 'FERNET_KEY'."
    Write-Host "Ejemplo: FERNET_KEY='$fernetKey'"
    Write-Host "------------------------------------------------------------------" -ForegroundColor Magenta
    Read-Host -Prompt "Presiona Enter cuando hayas guardado el archivo '.env' para continuar..."

    # --- FASE 3: CREACION DE LA BASE DE DATOS INICIAL ---
    Write-Host "`n[FASE 3/5] Inicializando la base de datos..." -ForegroundColor Yellow
    
    python -m seed.setup_data
    Write-Host "Base de datos inicializada correctamente." -ForegroundColor Green

    # --- FASE 4: VERIFICACION Y PRUEBAS ---
    Write-Host "`n[FASE 4/5] Ejecutando pruebas unitarias..." -ForegroundColor Yellow
    
    python -m pytest

    if ($LASTEXITCODE -ne 0) {
        throw "Las pruebas de Pytest han fallado. Revisa el log para mas detalles."
    }
    Write-Host "Todas las pruebas pasaron exitosamente." -ForegroundColor Green

    # --- FASE 5: EJECUCION DE LA APLICACION ---
    Write-Host "`n[FASE 5/5] ¡Configuracion completada!" -ForegroundColor Cyan
    Write-Host "Todo esta listo para empezar a desarrollar."
    Write-Host "Para iniciar el servidor, puedes ejecutar el script 'start_server.ps1' o el comando 'python -m app.main'."
    Write-Host "Servidor disponible en: http://127.0.0.1:5000" -ForegroundColor White

}
catch {
    Write-Host "`n[ERROR] Ocurrio un error durante la ejecucion del script." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Revisa el archivo '$LogFile' para un registro detallado." -ForegroundColor Red
}
finally {
    # Detener la transcripcion
    Stop-Transcript
}
