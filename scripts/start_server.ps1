# ==============================================================================
# Script: start_server.ps1
# Description: Inicia el servidor de desarrollo de Flask.
# Author: El checon
# ==============================================================================

# Iniciar transcripción para logging
$LogFile = "start_server.log"
Start-Transcript -Path $LogFile -Append

# Verificar que el script se ejecuta desde la raíz del proyecto
if (-not (Test-Path "requirements.txt") -or -not (Test-Path "app")) {
    Write-Host "[ERROR] Este script debe ser ejecutado desde la raíz del proyecto." -ForegroundColor Red
    Write-Host "Por favor, navega a la carpeta raíz y ejecuta el script así: .\scripts\start_server.ps1" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

try {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "INICIANDO SERVIDOR DE DESARROLLO" -ForegroundColor Cyan
    Write-Host "================================================"

    # 1. Verificar Entorno Virtual
    Write-Host "`nVerificando la existencia del entorno virtual..."
    if (-not (Test-Path "..\.venv\Scripts\Activate.ps1")) {
        throw "El entorno virtual no se encuentra. Por favor, ejecuta el script 'setup.ps1' primero."
    }
    Write-Host "Entorno virtual encontrado." -ForegroundColor Green

    # 2. Activar el Entorno Virtual
    Write-Host "Activando el entorno virtual..."
    . ..\.venv\Scripts\Activate.ps1
    Write-Host "Entorno activado." -ForegroundColor Green

    # 3. Iniciar la Aplicación Flask
    Write-Host "`nIniciando el servidor Flask..." -ForegroundColor Yellow
    Write-Host "Presiona CTRL+C para detener el servidor."
    Write-Host "El servidor estará disponible en: http://127.0.0.1:5000" -ForegroundColor White
    
    python -m app.main

}
catch {
    Write-Host "`n[ERROR] Ocurrió un error al intentar iniciar el servidor." -ForegroundColor Red
    Write-host $_.Exception.Message -ForegroundColor Red
    Write-Host "Revisa el archivo '$LogFile' para un registro detallado." -ForegroundColor Red
}
finally {
    # Detener la transcripción
    Write-Host "`nEl servidor se ha detenido."
    Stop-Transcript
}
