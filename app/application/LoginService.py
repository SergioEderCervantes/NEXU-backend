import logging
from typing import  List
from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
from app.repository.user_repository import UserRepository
from app.domain.entities import User, verify_password
from app.domain.exceptions import UserAlreadyExistsException, InvalidCredentialsException


logger = logging.getLogger('app')

class LoginService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def signup(self, raw_user_data: dict) -> User:
        """
        Registers a new user after checking for duplicates and filling in necessary data.
        Raises UserAlreadyExistsException if the email is already taken.
        """
        logger.info("Attempting to register a new user.")
        
        email = raw_user_data.get('email')
        if not email:
            logger.error("Signup failed: Email is missing from raw user data.")
            raise ValueError("Email is required.") # Use a more specific exception if needed
            
        # Check if user already exists by email
        if self.user_repository.find_by_email(email):
            logger.warning(f"Signup failed: user with email '{email}' already exists.")
            raise UserAlreadyExistsException()

        # Fill in system-managed data (like ID from email prefix, is_active)
        filled_data = self._fill_user_data(raw_user_data)
        
        # Create User entity. Pydantic's @model_validator handles password hashing automatically.
        new_user = User(**filled_data)
        
        self.user_repository.add(new_user)
        logger.info(f"Successfully registered user with ID: {new_user.id}, email: {new_user.email}")
        
        # TODO: Ahorita retorna el new user, pero se va a usar JWT, entonces se debe de regeresar eso
        return new_user

    def login(self, email: str, password: str) -> User:
        """
        Authenticates a user with provided email and password.
        Raises InvalidCredentialsException if authentication fails.
        """
        logger.info(f"Attempting to log in user with email: {email}")
        
        user = self.user_repository.find_by_email(email)
        if not user:
            logger.warning(f"Login failed: User with email '{email}' not found.")
            raise InvalidCredentialsException() # Don't specify if email or password was wrong for security

        # Verify the provided password against the stored hashed password
        if not verify_password(password, user.password):
            logger.warning(f"Login failed for user '{email}': incorrect password.")
            raise InvalidCredentialsException()

        logger.info(f"User '{email}' logged in successfully.")
        return user

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
        Password hashing is handled by the User entity's Pydantic validator.
        """
        # Ensure email is present before trying to extract ID
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
        
        # The Pydantic User model's @model_validator handles password hashing on instantiation.
        
        return raw_user_data

# Initialize dependencies for the LoginService
# These should ideally be injected, but for simplicity here they are instantiated directly.
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
login_service = LoginService(user_repository)
