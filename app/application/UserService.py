import logging
from typing import List
from app.domain.entities import User
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_all_users(self) -> List[User]:
        """
        Retrieves all users from the repository.
        """
        logger.info("Retrieving all users from the repository.")
        users = self.user_repository.find_all()
        return users
    

    def set_user_status(self, user_id: str, is_active: bool) -> None:
        """
        Sets the user's status to active or inactive.
        """
        logger.info(f"Setting user with ID {user_id} to is_active={is_active}")
        user = self.user_repository.find_by_id(user_id)
        if user:
            user.is_active = is_active
            self.user_repository.update(user)
            logger.info(f"Successfully updated status for user {user_id}")
        else:
            logger.warning(f"Could not set status for user {user_id}: User not found.")


# Initialize dependencies for the UserService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
user_service = UserService(user_repository)
