class ApplicationException(Exception):
    """Base class for application-specific exceptions."""
    @property
    def message(self):
        return 'An application error occurred.'

class UserNotFoundException(ApplicationException):
    """Raised when a user is not found in the repository."""
    @property
    def message(self):
        return 'User not found.'

class UserAlreadyExistsException(ApplicationException):
    """Raised when trying to create a user that already exists."""
    @property
    def message(self):
        return 'User with this email or username already exists.'

class InvalidCredentialsException(ApplicationException):
    """Raised when a login attempt fails due to incorrect credentials."""
    @property
    def message(self):
        return 'Invalid credentials provided.'

class InvalidPasswordException(ApplicationException):
    """Raised when a password is not valid."""
    @property
    def message(self):
        return 'Invalid password provided.'
