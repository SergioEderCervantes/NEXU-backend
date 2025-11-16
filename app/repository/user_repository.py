from typing import Optional
from app.domain.entities import User, DbFile
from app.repository.base_repository import BaseRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

class UserRepository(BaseRepository[User]):
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager):
        super().__init__(file_manager, encryption_manager, DbFile.USERS, 'usuarios')

    def _to_entity(self, item: dict) -> User:
        return User(**item)

    def find_by_username(self, username: str) -> Optional[User]:
        return self.find_by_attribute('nombre_usuario', username)

    def find_by_email(self, email: str) -> Optional[User]:
        return self.find_by_attribute('correo_electronico', email)
