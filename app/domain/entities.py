from enum import Enum
import os
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional, List
from app.config.settings import Config
from app.utils.hashing import hash_password
from datetime import datetime, date, timezone
import uuid

class DbFile(Enum):
    USERS = os.path.join(Config.BASE_PATH, "Usuarios.json.enc")
    CHATS = os.path.join(Config.BASE_PATH, "Chats.json.enc")
    MESSAGES = os.path.join(Config.BASE_PATH, "Mensajes.json.enc")
    POSTS = os.path.join(Config.BASE_PATH, "Publicaciones.json.enc")
    TAGS = os.path.join(Config.BASE_PATH, "Tags.json.enc")
    TEST = os.path.join(Config.BASE_PATH, "Test.json.enc")


class BaseEntity(BaseModel):
    id: str = Field(default="")
    @model_validator(mode='before')
    @classmethod
    def create_id(cls, data:Any) -> Any:
        """
        Crea el id unico con uuid v4 en caso de que se llegue sin id, que va a ser casi siempre
        """
        if isinstance(data, dict) and 'id' not in data:
            data['id'] = str(uuid.uuid4())
        return data    

class Tag(BaseEntity):
    name: str
    description: str

class User(BaseEntity):
    name: str
    email: str
    password: str
    is_active: bool = True
    career: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = Field(default_factory=date.today)
    bio: Optional[str] = None
    tag_ids: List[str] = Field(default_factory=list)
    avatar_url: Optional[str] = "https://res.cloudinary.com/dextv1cgm/image/upload/v1764717519/k0fahusthlf5lmhdjnkh.png"

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
    user_a: str
    user_b: str
    last_message_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='before')
    @classmethod
    def create_id(cls, data: Any) -> Any:
        """
        Crea un ID compuesto y determinístico para el chat basado en los IDs de los usuarios.
        Ordena los IDs de los usuarios para garantizar que el chat entre A y B tenga el mismo ID que entre B y A.
        """
        if isinstance(data, dict) and 'id' not in data:
            user_a = data.get('user_a')
            user_b = data.get('user_b')
            if not user_a or not user_b:
                raise ValueError("user_a and user_b must be provided to create a Chat")
            
            # Ordenar los IDs para consistencia
            sorted_users = sorted([user_a, user_b])
            data['id'] = f"{sorted_users[0]}-{sorted_users[1]}"
        return data


    
class Message(BaseEntity):
    conversation_id: str
    sender_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    delivered: bool

class Post(BaseEntity):
    user_id: str
    tag_id:str
    description:str
    timestamp:datetime = Field(default_factory=datetime.now)
