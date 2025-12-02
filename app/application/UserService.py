import logging
from typing import List
from app.domain.entities import User
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.application.upload_service import upload_service

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

    def get_user_by_id(self, user_id: str) -> User | None:
        """
        Retrieves a single user by their ID.
        """
        logger.info(f"Retrieving user with ID: {user_id}")
        user = self.user_repository.find_by_id(user_id)
        return user
    

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
    
    def upload_avatar(self, user_id: str, file) -> User:
        """
        Uploads a new avatar for a user and updates their profile.

        Args:
            user_id: The ID of the user whose avatar is being updated.
            file: The avatar file to upload.

        Returns:
            The updated User object with the new avatar URL.
            
        Raises:
            ValueError: If the user with the given ID is not found.
        """
        logger.info(f"Starting avatar upload process for user_id: {user_id}")
        user = self.get_user_by_id(user_id)
        if not user:
            logger.error(f"User with id: {user_id} not found for avatar upload.")
            raise ValueError("User not found")
        
        # Delegate the upload to the specialized service
        url = upload_service.upload_avatar(file, user_id)
        logger.info(f"Avatar uploaded to: {url}. Updating user profile.")
        
        # Update user's avatar URL and save
        user.avatar_url = url
        self.user_repository.update(user)
        logger.info(f"User {user_id} profile updated with new avatar.")
        
        return user


# Initialize dependencies for the UserService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
user_service = UserService(user_repository)
