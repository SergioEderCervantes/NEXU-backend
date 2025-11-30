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

## Estructura del proyecto

```
backend/
│
├── app/
│   ├── api/                     # Capa de presentación (HTTP / REST)
│   │   ├── __init__.py          # Registro global de Blueprints
│   │   └── user.py              # Endpoints relacionados a usuarios
│   │
│   ├── application/             # Capa de lógica de negocio (Servicios)
│   │   ├── __init__.py
│   │   ├── LoginService.py      # Lógica de autenticación y registro
│   │   └── UserService.py       # Lógica de gestión de usuarios
│   │
│   ├── repositories/            # Capa de acceso a datos (Repository Pattern)
│   │   ├── __init__.py
│   │   └── user_repository.py   # Lógica de lectura/escritura sobre JSON
│   │
│   ├── infraestructure/         # Capa de servicios de bajo nivel
│   │   ├── __init__.py
│   │   └── encryption_service.py # Encriptación y desencriptación de archivos
│   │
│   ├── config/                  # Núcleo de la aplicación
│   │   ├── __init__.py
│   │   ├── logger.py            # Logger central + decoradores de medición
│   │   └── config.py            # Configuraciones globales
│   │
│   ├── sockets/                 # Capa de comunicación en tiempo real
│   │   ├── __init__.py          # Inicializa Flask-SocketIO
│   │   └── chat.py              # Manejadores de eventos (mensajes, conexión)
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

| Capa | Responsabilidad | Comunicación con |
| :--- | :--- | :--- |
| **API** (`/app/api`) | Define los endpoints REST. Valida requests y delega la lógica de negocio a la capa de aplicación. | Application / Domain |
| **Sockets** (`/app/sockets`) | Maneja la comunicación en tiempo real (WebSockets). Delega la lógica a la capa de aplicación. | Application / Domain |
| **Application** (`/app/application`) | Contiene la lógica de negocio central. Orquesta las operaciones entre repositorios y otros servicios. | Repositories / Domain |
| **Repositories** (`/app/repositories`) | Implementan el patrón **Repository**. Abstraen el origen de datos y exponen métodos para acceder y manipularlos. | Infrastructure / Domain |
| **Infrastructure** (`/app/infraestructure`) | Maneja operaciones de bajo nivel como la manipulación de archivos (NFS) y la encriptación/desencriptación. | - |
| **Domain** (`app/domain`) | Define las entidades, excepciones y lógica de dominio de la aplicación. | Todas las capas |
| **Config** (`/app/config`) | Configuración, logging, scheduling y utilidades comunes. | Todas las capas |
| **Data (NFS)** (`/db`) | Capa física de persistencia. Contiene los JSON cifrados. | Infrastructure |

---

## ⚙️ Flujo interno simplificado

```text
Frontend / App Móvil
        │
        ▼
   [ Flask API ]  ←→  [ Flask-SocketIO (WebSockets) ]
        │
        ▼
   [ Application Layer (Services) ]
        │
        ▼
   [ Repository Pattern ]
        │
        ▼
 [ Encryption / Decryption ]
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

## Ejecucion de test con coverage:

```bash
     python -m pytest --cov=app --cov-report=html --cov-report=term-missing
```

-> Si lo quieres con Docker:

```bash
     docker compose exec python -m pytest --cov=app --cov-report=html --cov-report=term-missing
```


<!-- ## 🧩 Roadmap

* [ ] Añadir tests automáticos (pytest).

* [ ] Entender e implementar encriptacion y desencriptacion
* [ ] Crear una seed de datos para trabajar
* [ ] Implementar capa de queries JSON con jsonpath-ng.
* [ ] Implementar Patron repository
* [ ] Añadir objetos de dominio (serialización/deserialización).
* [ ] Hacer API REST
* [ ] Implementar chat con websockets
* [ ] Conectar servicio de notificaciones vía WebSockets.
* [ ] Implementar cron jobs de limpieza.
 -->
