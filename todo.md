# Pasos a resolver para el login:
- Ya todo esta hecho, ya solo falta hacer test del login, y documentacion de los endpoints disponibles

# Seed para que los frontends no tengan problema setteando el server
Hace falta un sistema de bash o ps1 que:
- Generar un ambiente de python e instale dependencias (maybe solo las necesarias para que fernet funcione si se hace el deploy en docker)
- Generar una llave de encriptacion para fernet (el seed/get_fist_key.py)
- Crear y llenar el .env en base al .env.example con la key de fernet
- Ejecutar una seed que inicialice el json encriptado vacio de usuarios (el seed/setup-data.py)
- Construir y ejecutar la imagen de docker
- Con el contenedor arriba, correr los test dentro del contenedor de docker (docker compose exec backend python -m pytest)
- Si algo falla, sacar un buen log para que me lo pasen y checar que todo bien

