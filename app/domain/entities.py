from enum import Enum
import os
from pydantic import BaseModel, Field
from typing import List, Optional

# TODO: quitar el getEnv de aqui, la constante se debe de importar desde settings.py
BASE_PATH = os.getenv("NFS_PATH", "db")

class DbFile(Enum):
    USERS = os.path.join(BASE_PATH, "Usuarios.json.enc")
    CHATS = os.path.join(BASE_PATH, "Chats.json.enc")
    SKILLS = os.path.join(BASE_PATH, "Habilidades.json.enc")
    REPUTATION = os.path.join(BASE_PATH, "Reputacion.json.enc")
    REQUESTS = os.path.join(BASE_PATH, "Solicitudes.json.enc")
    TAGS = os.path.join(BASE_PATH, "Tags.json.enc")

class BaseEntity(BaseModel):
    id: int = Field(..., gt=0)

class User(BaseEntity):
    nombre_usuario: str
    correo_electronico: str
    contrasena_hash: str
    nombre_completo: str
    biografia: Optional[str] = None
    habilidades: List[int] = []
    reputacion: int = 0
    tags: List[int] = []