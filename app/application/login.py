from typing import Any
from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
from app.repository.user_repository import UserRepository
from app.domain.entities import User
import logging
from app.utils.hashing import hash_password

logger = logging.getLogger('app')

file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)

def retrieve_users() -> list[dict[str, Any]]:
    users = user_repository.find_all()
    # Pydantic models must be converted to dicts for JSON serialization
    users_dict = [user.model_dump() for user in users]
    return users_dict

def create_user(raw_user_data: dict) -> bool:
    
    try:
        # TODO: manejo de excepciones: si no esta bien formateado el json, si ya existe el user, si no cumple con los campos
        email = raw_user_data['email']
        is_repeated = user_repository.find_by_email(email)
        if is_repeated is not None:
            raise Exception("Email ya existe")
        raw_user_data = fill_user_data(raw_user_data)
        # Creamos el user
        new_user = User(**raw_user_data)
        # Lo guardamos en la persistencia
        user_repository.add(new_user)
        return True
    except Exception as e:
        raise Exception(e)
    
    
def fill_user_data(raw_user_data:dict)-> dict:
    if isinstance(raw_user_data, dict) and "password" in raw_user_data:
        # Solo hashea si la contraseña no parece ya hasheada
        if not raw_user_data["password"].startswith("$2b"):
            raw_user_data["password"] = hash_password(raw_user_data["password"])
    if isinstance(raw_user_data, dict) and "email" in raw_user_data:
        email: str = raw_user_data["email"]
        email = email.split("@")[0]
        identifier = email.removeprefix("al")
        raw_user_data['id'] = int(identifier)
    raw_user_data['is_active'] = True
    return raw_user_data