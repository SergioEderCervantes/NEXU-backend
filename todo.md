# Plan de Acción: Script de Inicialización del Proyecto (`setup.ps1`)

Este documento define los pasos para crear un script de PowerShell (`.ps1`) que automatice la configuración inicial del proyecto para los desarrolladores en un entorno Windows.

---

### **Objetivo General**

Crear un único script `setup.ps1` que un desarrollador pueda ejecutar para tener un entorno de desarrollo funcional y listo para usar. El script debe ser robusto, proporcionar retroalimentación clara y manejar errores de manera efectiva.

---

### **Fase 1: Preparación y Entorno Virtual**

El script debe primero preparar el entorno de Python.

1.  **Verificar Python:**
    *   **Acción:** Comprobar que Python está instalado y disponible en el PATH.
    *   **Comando:** `Get-Command python`
    *   **Lógica:** Si no se encuentra, el script debe detenerse y notificar al usuario que necesita instalar Python.

2.  **Crear Entorno Virtual:**
    *   **Acción:** Crear una carpeta para el entorno virtual llamada `.venv` en la raíz del proyecto.
    *   **Comando:** `python -m venv .venv`
    *   **Lógica:** Verificar si la carpeta `.venv` ya existe para no repetir este paso innecesariamente.

3.  **Activar el Entorno Virtual:**
    *   **Acción:** Activar el entorno virtual para los siguientes comandos del script.
    *   **Comando (PowerShell):** `.\.venv\Scripts\Activate.ps1`

4.  **Instalar Dependencias:**
    *   **Acción:** Instalar todas las librerías de Python requeridas.
    *   **Comando:** `pip install -r requirements.txt`
    *   **Lógica:** Redirigir la salida para poder revisarla en caso de error.

---

### **Fase 2: Generación de Clave y Configuración del `.env`**

Esta fase se encarga de los secretos y la configuración del entorno.

1.  **Generar Clave de Encriptación:**
    *   **Acción:** Ejecutar el script `gen_first_key.py` para generar una nueva clave Fernet.
    *   **Comando:** `python .\seed\gen_first_key.py`
    *   **Lógica:** Capturar la clave generada (salida estándar del script) en una variable de PowerShell.

2.  **Manejo del Archivo `.env`:**
    *   **Acción:** Copiar `.env.example` a un nuevo archivo `.env` si este último no existe.
    *   **Comando:** `Copy-Item -Path .\.env.example -Destination .\.env -ErrorAction SilentlyContinue`
    *   **Lógica:** El script informará al usuario que se ha creado un archivo `.env` y le pedirá que lo configure.

3.  **Instruir al Usuario:**
    *   **Acción:** Mostrar un mensaje claro al usuario.
    *   **Mensaje:**
        ```
        ------------------------------------------------------------------
        [ACCIÓN REQUERIDA]
        Se ha generado una nueva clave de encriptación:
        
        CLAVE: [Aquí se muestra la clave generada en el paso 1]
        
        Por favor, abre el archivo `.env` que se acaba de crear y pega esta clave en la variable `FERNET_KEY`.
        
        Presiona Enter cuando hayas terminado para continuar con el script...
        ------------------------------------------------------------------
        ```
    *   **Comando:** `Read-Host` para pausar la ejecución hasta que el usuario presione Enter.

---

### **Fase 3: Creación de la Base de Datos Inicial**

Con la configuración lista, el script inicializará los archivos de datos.

1.  **Ejecutar el Script de Setup:**
    *   **Acción:** Correr `setup_data.py` para crear el archivo `Usuarios.json.enc` vacío y encriptado.
    *   **Comando:** `python .\seed\setup_data.py`
    *   **Lógica:** Este script depende de que la variable `FERNET_KEY` ya esté configurada en el `.env`, por eso la pausa en la fase anterior es crucial.

---

### **Fase 4: Verificación y Pruebas**

Para asegurar que todo se configuró correctamente.

1.  **Ejecutar Pruebas Unitarias:**
    *   **Acción:** Lanzar el conjunto de pruebas con `pytest`.
    *   **Comando:** `pytest`
    *   **Lógica:** Capturar la salida y el código de salida. Si las pruebas fallan, el script debe detenerse e informar del error.

---

### **Fase 5: Ejecución de la Aplicación**

El último paso es iniciar el servidor de desarrollo.

1.  **Iniciar la Aplicación Flask:**
    *   **Acción:** Ejecutar la aplicación principal.
    *   **Comando:** `flask run` (o `python -m app.main` si está configurado para ello).
    *   **Lógica:** Mostrar un mensaje final indicando que el servidor se ha iniciado y en qué URL está disponible (ej. `http://127.0.0.1:5000`).

---

### **Manejo de Errores y Logging**

El script debe ser robusto y fácil de depurar.

1.  **Logs:**
    *   **Acción:** Utilizar `Start-Transcript -Path setup.log` al inicio del script y `Stop-Transcript` al final (o en caso de error).
    *   **Lógica:** Esto guardará toda la salida de la consola en un archivo `setup.log`. Si algo falla, el desarrollador puede simplemente enviar este archivo para su revisión.
2.  **Salida Clara:**
    *   **Acción:** Usar `Write-Host` con colores para indicar los pasos (`-ForegroundColor Green` para éxito, `Yellow` para advertencias, `Red` para errores).
    *   **Lógica:** Guiar visualmente al usuario a través del proceso de configuración.

---

# Plan de Acción: Script para Iniciar el Servidor (`start_server.ps1`)

Este documento define los pasos para crear un script de PowerShell (`.ps1`) que inicie el servidor de desarrollo de manera rápida, asumiendo que el proyecto ya ha sido configurado previamente con `setup.ps1`.

---

### **Objetivo General**

Crear un script `start_server.ps1` que un desarrollador pueda ejecutar para activar el entorno virtual y levantar el servidor Flask con un solo comando.

---

### **Pasos Detallados**

1.  **Verificar Entorno Virtual:**
    *   **Acción:** Comprobar que el entorno virtual `.venv` existe.
    *   **Comando:** `Test-Path .\.venv\Scripts\Activate.ps1`
    *   **Lógica:** Si el entorno virtual no existe, el script debe notificar al usuario que necesita ejecutar `setup.ps1` primero y luego detenerse.

2.  **Activar el Entorno Virtual:**
    *   **Acción:** Activar el entorno virtual para los comandos subsiguientes.
    *   **Comando (PowerShell):** `.\.venv\Scripts\Activate.ps1`

3.  **Cargar Variables de Entorno:**
    *   **Acción:** Asegurarse de que las variables del `.env` (como `FLASK_APP` y `FERNET_KEY`) estén cargadas en la sesión actual.
    *   **Comando:** PowerShell suele cargar `.env` automáticamente si `python-dotenv` está configurado en la aplicación. No es necesario un paso explícito si la aplicación ya lo maneja. Si no, se podría usar `(Get-Content .env | ForEach-Object { $key, $value = $_.Split('=', 2); Set-Item -Path Env:$key -Value $value })`.

4.  **Iniciar la Aplicación Flask:**
    *   **Acción:** Ejecutar la aplicación principal del servidor Flask.
    *   **Comando:** `flask run`
    *   **Lógica:** Se ejecutará en primer plano para que el usuario vea la salida del servidor.

---

### **Manejo de Errores y Salida**

1.  **Mensajes Claros:**
    *   **Acción:** Usar `Write-Host` para informar sobre el estado del servidor (iniciado, en qué URL).
    *   **Lógica:** Indicar que el servidor se está iniciando y proporcionar la URL de acceso por defecto (ej. `http://127.00.1:5000`).
2.  **Logging Básico:**
    *   **Acción:** Envolver la ejecución del servidor en un bloque `try-catch` si se desea un manejo de errores más sofisticado, aunque `flask run` ya proporciona buena salida.
    *   **Comando:** Opcional: `Start-Transcript -Path start_server.log -Append` al inicio, y `Stop-Transcript` en `finally` o al final.

