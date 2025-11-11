# 🧩 Backend de NEXU: Servidor Flask con encriptacion, lectura de json, API REST, etc

## 🚀 Descripción general

Este proyecto es un backend modular desarrollado con **Flask** y **Flask-SocketIO**, diseñado para operar utilizando **archivos JSON encriptados montados en un cliente NFS**.

El sistema implementa una arquitectura por capas, con separación clara entre responsabilidades y soporte para:

* Repositorios sobre JSON.
* Encriptación/desencriptación de datos.
* WebSockets para chat 
* Logging robusto con medición de tiempos.
* Tareas programadas (cron jobs) de mantenimiento y limpieza.

---

##  Estructura del proyecto

```
backend/
│
├── app/
│   ├── api/                     # Capa de presentación (HTTP / REST)
│   │   ├── __init__.py          # Registro global de Blueprints
│   │   ├── user.py       # Endpoints relacionados a usuarios
│   │   ├── chat.py       # Endpoints relacionados al chat
│   │   └── system.py     # Otros endpoints del sistema
│   │
│   ├── repositories/            # Capa de acceso a datos (Repository Pattern)
│   │   ├── __init__.py
│   │   └── user_repository.py   # Lógica de lectura/escritura sobre JSON
│   │
│   ├── infraestructure/         # Capa de Servicios para la lectura de los archivos dek nfs
│   │   ├── __init__.py
│   │   └── encryption_service.py # Encriptación y desencriptación de archivos
│   │
│   ├── config/                  # Núcleo de la aplicación
│   │   ├── __init__.py
│   │   ├── logger.py            # Logger central + decoradores de medición
│   │   ├── config.py            # Configuraciones globales
│   │   └── scheduler.py         # Registro y control de tareas programadas
│   │
│   ├── sockets/                 # Capa de comunicación en tiempo real
│   │   ├── __init__.py          # Inicializa Flask-SocketIO
│   │   └── chat_socket.py       # Manejadores de eventos (mensajes, conexión)
│   │
│   ├── main.py                  # Punto de entrada principal del servidor Flask
│   └── wsgi.py                  # Entrada para servidores WSGI (gunicorn)
│
├── db/                        # Archivos JSON encriptados (montados por NFS)
│
├── logs/                        # Archivos de logs del sistema
│
├── Dockerfile                   # Definición de la imagen base del backend
├── docker-compose.yml            # Orquestación de servicios 
└── requirements.txt              # Dependencias del proyecto
```

---

## 🧱 Comportamiento de las capas

| Capa                                   | Responsabilidad                                                                                                                | Comunicación con        |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| **API** (`/app/api`)                   | Define los endpoints REST que consumen el frontend o móvil. Valida requests y delega la lógica a los repositorios o servicios. | Domain / Repositories |
| **Sockets** (`/app/sockets`)           | Maneja la comunicación en tiempo real (chat, notificaciones, etc.) vía WebSockets.                                             | Domain / Repositories                 |
| **Repositories** (`/app/repositories`) | Implementan el patrón **Repository**. Acceden, consultan y manipulan los JSON desencriptados.                                  | Infraestructure / API          |
| **Infraestructure** (`/app/Infraestructure`)         | Capa encargada del manejo a bajo nivel de la persistencia de los datos json (lectura del de archivos desde el NFS y encriptacion/desencriptacion)| Repositories            |
| **config** (`/app/config`)                 | Configuración, logging, scheduling y utilidades comunes.                                                                       | Todas las capas         |
| **Domain** (`app/domain`)| Define todo lo relacionado en el dominio de la aplicacion, desde objetos de dominio, hasta logica especial | Todas las capas |
| **Data (NFS)** (`/db`)               | Capa física de persistencia. Contiene los JSON cifrados que representan la “base de datos”.                                    | Infraestructure            |

---

## ⚙️ Flujo interno simplificado

```text
Frontend / App Móvil
        │
        ▼
   [ Flask API ]  ←→  [ Flask-SocketIO (WebSockets) ]
        │
        ▼
   [ Repository Pattern ]
        │
        ▼
 [ Encriptación / Desencriptación ]
        │
        ▼
 [ Archivos JSON en cliente NFS ]
```

---

## 🧩 Logger y medición de tareas

Cada acción registrada (lectura, desencriptación, consulta, escritura, etc.) genera una entrada en los logs del sistema:

```
2025-11-10 14:20:01 - INFO - [app_logger] - Aplicación Flask inicializada correctamente
2025-11-10 14:20:03 - INFO - [app_logger] - Tarea 'read_user_data' ejecutada en 0.052s
```

Los logs se almacenan en `/logs/app.log`, montado en el host para análisis externo.

---

## 🕒 Cron Jobs y tareas programadas

Las tareas automáticas se definen en `app/config/scheduler.py` y pueden incluir:

* Limpieza de archivos temporales.
* Reindexación de JSONs.
* Validación de integridad.
* Backup o rotación de logs.

---

## 🧰 Instalación y ejecución

### 1️⃣ Clonar el repositorio


### 2️⃣ Construir la imagen y levantar servicios

```bash
docker compose up --build
```

### 3️⃣ Acceder a la API

```
http://localhost:5000/health
```

Si esto funciona, el servidor esta ejecutandose!, revisa el `app/api/__init__.py` para ver las demas rutas a la api

---
<!-- 
## 🧩 Variables de entorno útiles

| Variable         | Descripción                                   | Ejemplo                      |
| ---------------- | --------------------------------------------- | ---------------------------- |
| `FLASK_ENV`      | Modo de ejecución                             | `development` / `production` |
| `LOG_LEVEL`      | Nivel de logging                              | `INFO`, `DEBUG`, `ERROR`     |
| `ENCRYPTION_KEY` | Clave usada para cifrar/descifrar JSONs       | *(defínela en .env)*         |
| `NFS_PATH`       | Punto de montaje NFS donde viven los archivos | `/mnt/nfs/json_data`         |

--- -->

## 🧠 Tecnologías principales

* **Flask 3.x** — servidor web principal.
* **Flask-SocketIO** — WebSockets y eventos en tiempo real.
* **jsonpath-ng** — consultas dinámicas sobre estructuras JSON.
* **cryptography** — encriptación de archivos.
* **APScheduler** — tareas periódicas.
* **Docker Compose** — orquestación de servicios.

---


<!-- ## 🧩 Roadmap

* [ ] Implementar capa de queries JSON con JMESPath.
* [ ] Añadir objetos de dominio (serialización/deserialización).
* [ ] Agregar capa de autenticación JWT.
* [ ] Conectar servicio de notificaciones vía WebSockets.
* [ ] Implementar cron jobs de limpieza.
* [ ] Añadir tests automáticos (pytest).
 -->
