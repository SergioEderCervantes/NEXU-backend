import logging
from typing import List
from app.domain.entities import User
from app.repository.user_repository import UserRepository
from app.repository.tag_repository import TagRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.application.upload_service import upload_service

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository, tag_repository: TagRepository):
        self.user_repository = user_repository
        self.tag_repository = tag_repository
        self._tags_cache = None

    def _get_all_tags(self):
        if self._tags_cache is None:
            logger.info("Caching all tags.")
            self._tags_cache = self.tag_repository.find_all()
        return self._tags_cache

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

    def get_user_profile(self, user: User) -> dict:
        """
        Returns a dictionary representation of the user with tag names and icons populated
        instead of tag IDs.
        """
        user_dict = user.model_dump(exclude={'password'})
        
        all_tags = self._get_all_tags()
        tags_map = {tag.id: tag.name for tag in all_tags}

        # Replace tag_ids with the actual names
        tag_names = [tags_map.get(tag_id) for tag_id in user.tag_ids]

            
        user_dict['tags'] = tag_names
        del user_dict['tag_ids']  # Remove the original tag_ids field
        
        return user_dict

    def update_user_profile(self, user_id: str, data: dict) -> User:
        """
        Updates a user's profile with the given data.
        Only 'name', 'career', 'date_of_birth', and 'tag_ids' are updatable.
        """
        logger.info(f"Updating profile for user with ID: {user_id}")
        user = self.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found for profile update.")
            raise ValueError("User not found")

        # Update only the allowed fields if they are present in the data
        if "name" in data:
            user.name = data["name"]
        if "career" in data:
            user.career = data["career"]
        if "date_of_birth" in data:
            user.date_of_birth = data["date_of_birth"]
        if "tag_ids" in data:
            user.tag_ids = data["tag_ids"]
        if "gender" in data:
            user.gender = data["gender"]

        self.user_repository.update(user)
        logger.info(f"Successfully updated profile for user {user_id}")
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
tag_repository = TagRepository(file_manager, encryption_manager)
user_service = UserService(user_repository, tag_repository)
