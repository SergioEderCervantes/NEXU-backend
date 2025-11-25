import logging
import jwt
from datetime import datetime, timedelta
from typing import List
from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
from app.repository.user_repository import UserRepository
from app.domain.entities import User, verify_password
from app.domain.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from app.config.settings import Config

logger = logging.getLogger('app')

class LoginService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def _create_access_token(self, user_id: int) -> str:
        """
        Generates a new JWT access token.
        """
        to_encode = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        encoded_jwt = jwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM) # type: ignore
        return encoded_jwt

    def signup(self, raw_user_data: dict) -> str:
        """
        Registers a new user and returns a JWT access token upon successful creation.
        """
        logger.info("Attempting to register a new user.")
        
        email = raw_user_data.get('email')
        if not email:
            logger.error("Signup failed: Email is missing from raw user data.")
            raise ValueError("Email is required.")
            
        if self.user_repository.find_by_email(email):
            logger.warning(f"Signup failed: user with email '{email}' already exists.")
            raise UserAlreadyExistsException()

        filled_data = self._fill_user_data(raw_user_data)
        new_user = User(**filled_data)
        
        self.user_repository.add(new_user)
        logger.info(f"Successfully registered user with ID: {new_user.id}, email: {new_user.email}")
        
        # Generate a token for the new user
        return self._create_access_token(user_id=new_user.id)

    def login(self, email: str, password: str) -> str:
        """
        Authenticates a user and returns a JWT access token upon success.
        """
        logger.info(f"Attempting to log in user with email: {email}")
        
        user = self.user_repository.find_by_email(email)
        if not user:
            logger.warning(f"Login failed: User with email '{email}' not found.")
            raise InvalidCredentialsException()

        if not verify_password(password, user.password):
            logger.warning(f"Login failed for user '{email}': incorrect password.")
            raise InvalidCredentialsException()

        logger.info(f"User '{email}' logged in successfully.")
        
        # Generate and return the token
        return self._create_access_token(user_id=user.id)

    def get_all_users(self) -> List[User]:
        """
        Retrieves all users from the repository.
        """
        logger.info("Retrieving all users from the repository.")
        users = self.user_repository.find_all()
        return users

    def _fill_user_data(self, raw_user_data: dict) -> dict:
        """
        Fills in system-managed user data like ID from email prefix and active status.
        """
        email = raw_user_data.get('email')
        if email:
            try:
                email_prefix = email.split('@')[0]
                identifier = email_prefix.removeprefix('al')
                raw_user_data['id'] = int(identifier)
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to extract user ID from email '{email}': {e}")
                raise ValueError("Could not determine user ID from email format.")
        else:
            logger.warning("Attempted to fill user data without an email field.")
            raise ValueError("Email is required for ID generation.")

        raw_user_data['is_active'] = True
        return raw_user_data

# Initialize dependencies for the LoginService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
login_service = LoginService(user_repository)
