from enum import Enum
import os
from pydantic import BaseModel, Field
from typing import  Optional
from app.config.settings import Config


class DbFile(Enum):
    USERS = os.path.join(Config.BASE_PATH, "Usuarios.json.enc")
    CHATS = os.path.join(Config.BASE_PATH, "Chats.json.enc")
    SKILLS = os.path.join(Config.BASE_PATH, "Habilidades.json.enc")
    REPUTATION = os.path.join(Config.BASE_PATH, "Reputacion.json.enc")
    REQUESTS = os.path.join(Config.BASE_PATH, "Solicitudes.json.enc")
    TAGS = os.path.join(Config.BASE_PATH, "Tags.json.enc")


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

