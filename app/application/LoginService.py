import logging
import jwt
from datetime import datetime, timedelta
import uuid # New import
from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
from app.repository.user_repository import UserRepository
from app.domain.entities import User
from app.utils.hashing import verify_password
from app.domain.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from app.config.settings import Config
from app.application.UserService import user_service, UserService

logger = logging.getLogger('app')

class LoginService:
    def __init__(self, user_repository: UserRepository, user_service: UserService):
        self.user_repository = user_repository
        self.user_service = user_service

    def _create_access_token(self, user_id: str) -> str:
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

        new_user = User(**raw_user_data)
        
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

        # Setting user status as active
        self.user_service.set_user_status(user.id, True)
        
        logger.info(f"User '{email}' logged in successfully.")
        
        # Generate and return the token
        return self._create_access_token(user_id=user.id)



# Initialize dependencies for the LoginService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
login_service = LoginService(user_repository, user_service)
