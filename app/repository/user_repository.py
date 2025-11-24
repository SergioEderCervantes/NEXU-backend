from typing import Optional
from app.domain.entities import User, DbFile
from app.repository.base_repository import BaseRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

class UserRepository(BaseRepository[User]):
    """
    UserRepository is a concrete implementation of BaseRepository specifically for User entities.
    It handles CRUD operations for User objects, leveraging the generic functionality
    provided by BaseRepository and implementing User-specific search methods.
    """
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager):
        """
        Initializes the UserRepository.

        Args:
            file_manager (FileManager): Service to handle file read/write operations.
            encryption_manager (EncryptionManager): Service to handle data encryption/decryption.
        """
        super().__init__(file_manager, encryption_manager, DbFile.USERS, 'users')

    def _to_entity(self, item: dict) -> User:
        """
        Converts a dictionary representation of a user into a User domain entity object.

        Args:
            item (dict): A dictionary containing user data.

        Returns:
            User: A User domain entity.
        """
        return User(**item)

    def find_by_username(self, username: str) -> Optional[User]:
        """
        Finds a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            Optional[User]: The User entity if found, otherwise None.
        """
        return self.find_by_attribute('name', username)

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Finds a user by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Optional[User]: The User entity if found, otherwise None.
        """
        return self.find_by_attribute('email', email)
