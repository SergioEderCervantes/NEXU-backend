import pytest
from unittest.mock import MagicMock
from app.application.UserService import UserService
from app.domain.entities import User

@pytest.fixture
def mock_user_repository():
    """Fixture to create a mock user repository."""
    return MagicMock()

@pytest.fixture
def user_service(mock_user_repository):
    """Fixture to create a UserService with a mock repository."""
    return UserService(mock_user_repository)

def test_get_all_users(user_service, mock_user_repository):
    """
    GIVEN a UserService
    WHEN the get_all_users method is called
    THEN it should call the repository's find_all method and return the result.
    """
    # Arrange
    mock_users = [
        User(id="1", name="Test User 1", email="test1@example.com", password="password1", is_active=True, gender="other"),
        User(id="2", name="Test User 2", email="test2@example.com", password="password2", is_active=False, gender="other"),
    ]
    mock_user_repository.find_all.return_value = mock_users

    # Act
    users = user_service.get_all_users()

    # Assert
    mock_user_repository.find_all.assert_called_once()
    assert users == mock_users
    assert len(users) == 2



def test_set_user_status_active(user_service, mock_user_repository):
    """
    GIVEN a UserService and an existing user
    WHEN the set_user_status method is called to set the user as active
    THEN it should update the user's status and call the repository's update method.
    """
    # Arrange
    user_id = "1"
    mock_user = User(id=user_id, name="Test User", email="test@example.com", password="password", is_active=False, gender="female")
    mock_user_repository.find_by_id.return_value = mock_user

    # Act
    user_service.set_user_status(user_id, True)

    # Assert
    mock_user_repository.find_by_id.assert_called_once_with(user_id)
    assert mock_user.is_active is True
    mock_user_repository.update.assert_called_once_with(mock_user)

def test_set_user_status_inactive(user_service, mock_user_repository):
    """
    GIVEN a UserService and an existing user
    WHEN the set_user_status method is called to set the user as inactive
    THEN it should update the user's status and call the repository's update method.
    """
    # Arrange
    user_id = "1"
    mock_user = User(id=user_id, name="Test User", email="test@example.com", password="password", is_active=True, gender="other")
    mock_user_repository.find_by_id.return_value = mock_user

    # Act
    user_service.set_user_status(user_id, False)

    # Assert
    mock_user_repository.find_by_id.assert_called_once_with(user_id)
    assert mock_user.is_active is False
    mock_user_repository.update.assert_called_once_with(mock_user)

def test_set_user_status_user_not_found(user_service, mock_user_repository):
    """
    GIVEN a UserService
    WHEN the set_user_status method is called for a non-existent user
    THEN it should not call the repository's update method.
    """
    # Arrange
    user_id = 999
    mock_user_repository.find_by_id.return_value = None

    # Act
    user_service.set_user_status(user_id, True)

    # Assert
    mock_user_repository.find_by_id.assert_called_once_with(user_id)
    mock_user_repository.update.assert_not_called()
