from enum import Enum
import os
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional
from app.config.settings import Config
from app.utils.hashing import hash_password
from datetime import datetime


class DbFile(Enum):
    USERS = os.path.join(Config.BASE_PATH, "Usuarios.json.enc")
    CHATS = os.path.join(Config.BASE_PATH, "Chats.json.enc")
    MESSAGES = os.path.join(Config.BASE_PATH, "Mensajes.json.enc")
    SKILLS = os.path.join(Config.BASE_PATH, "Habilidades.json.enc")
    TAGS = os.path.join(Config.BASE_PATH, "Tags.json.enc")
    TEST = os.path.join(Config.BASE_PATH, "Test.json.enc")


class BaseEntity(BaseModel):
    id: int = Field(..., gt=0)


class User(BaseEntity):
    name: str
    email: str
    password: str
    is_active: bool
    gender: str
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


class Chat(BaseEntity):
    user_a: int
    user_b: int
    last_message_at: datetime = Field(default_factory=datetime.now)
    
class Message(BaseEntity):
    conversation_id: int
    sender_id: int
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    delivered: bool
