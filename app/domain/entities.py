from enum import Enum
import os


# TODO: quitar el getEnv de aqui, la constante se debe de importar desde settings.py
BASE_PATH = os.getenv("NFS_PATH", "db")

class DbFile(Enum):
    USERS = os.path.join(BASE_PATH, "Usuarios.json.enc")
    CHATS = os.path.join(BASE_PATH, "Chats.json.enc")                                                                      
    SKILLS = os.path.join(BASE_PATH, "Habilidades.json.enc")                                                               
    REPUTATION = os.path.join(BASE_PATH, "Reputacion.json.enc")
    REQUESTS = os.path.join(BASE_PATH, "Solicitudes.json.enc")
    TAGS = os.path.join(BASE_PATH, "Tags.json.enc")