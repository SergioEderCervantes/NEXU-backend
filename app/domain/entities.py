from enum import Enum
import os
import bcrypt
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional
from app.config.settings import Config


# --- Implementación Segura de Contraseñas con bcrypt ---

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt. Genera un salt y devuelve el hash completo en un solo string.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash de bcrypt.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except ValueError:
        # This can happen if the stored hash is not a valid bcrypt hash
        return False

# -------------------------------------------------------------------------


class DbFile(Enum):
    USERS = os.path.join(Config.BASE_PATH, "Usuarios.json.enc")
    CHATS = os.path.join(Config.BASE_PATH, "Chats.json.enc")
    SKILLS = os.path.join(Config.BASE_PATH, "Habilidades.json.enc")
    REPUTATION = os.path.join(Config.BASE_PATH, "Reputacion.json.enc")
    REQUESTS = os.path.join(Config.BASE_PATH, "Solicitudes.json.enc")
    TAGS = os.path.join(Config.BASE_PATH, "Tags.json.enc")
    TEST = os.path.join(Config.BASE_PATH, "Test.json.enc")


class BaseEntity(BaseModel):
    id: int = Field(..., gt=0)


class User(BaseEntity):
    name: str
    email: str
    password: str
    is_active: bool
    gender: str = "No especificado"
    bio: Optional[str] = None
    reputation: int = 0

    @model_validator(mode='before')
    @classmethod
    def hash_password_on_creation(cls, data: Any) -> Any:
        """
        Este validador se asegura de que la contraseña SIEMPRE esté hasheada.
        - Si la contraseña no está hasheada (al crear un usuario), la hashea.
        - Si la contraseña ya está hasheada (al cargar desde la BD), no hace nada.
        """
        if isinstance(data, dict) and 'password' in data:
            password = data['password']
            # Los hashes de bcrypt siempre empiezan con '$2b$' (o similar) y tienen 60 caracteres.
            if not (isinstance(password, str) and password.startswith('$2b$') and len(password) == 60):
                data['password'] = hash_password(password)
        return data

