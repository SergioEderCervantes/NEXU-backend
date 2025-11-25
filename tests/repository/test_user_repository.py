import pytest
import json
from unittest.mock import MagicMock
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import User, DbFile

@pytest.fixture
def mock_file_manager():
    """Mock for FileManager."""
    return MagicMock(spec=FileManager)

@pytest.fixture
def mock_encryption_manager():
    """Mock for EncryptionManager."""
    return MagicMock(spec=EncryptionManager)

@pytest.fixture
def user_repository(mock_file_manager, mock_encryption_manager):
    """Fixture for UserRepository with mocked dependencies."""
    return UserRepository(mock_file_manager, mock_encryption_manager)

@pytest.fixture
def sample_users_data():
    """Sample user data that mimics the structure in the JSON file."""
    return {
        "users": [
            {
                "id": 1,
                "name": "Test User One",
                "email": "test1@example.com",
                "password": "hashed_password1",
                "is_active": True,
                "gender": "male",
                "bio": "Bio for user 1.",
                "reputation": 10,
            },
            {
                "id": 2,
                "name": "Test User Two",
                "email": "test2@example.com",
                "password": "hashed_password2",
                "is_active": False,
                "gender": "female",
                "bio": "Bio for user 2.",
                "reputation": 20,
            }
        ]
    }

def setup_mocks(mock_file_manager, mock_encryption_manager, data):
    """Helper to configure mocks for reading data."""
    json_data = json.dumps(data)
    encrypted_data = b'encrypted_data_mock'
    
    mock_file_manager.read_file.return_value = encrypted_data
    mock_encryption_manager.decrypt_data.return_value = json_data
    mock_encryption_manager.encrypt_data.return_value = b'new_encrypted_data'

# --- Repository Tests ---

def test_find_all(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test finding all users."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    users = user_repository.find_all()
    
    assert len(users) == 2
    assert isinstance(users[0], User)
    assert users[0].id == 1
    assert users[1].name == "Test User Two"
    mock_file_manager.read_file.assert_called_once_with(DbFile.USERS)
    mock_encryption_manager.decrypt_data.assert_called_once_with(b'encrypted_data_mock')

def test_find_by_id(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test finding a user by ID."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    user = user_repository.find_by_id(2)
    
    assert user is not None
    assert isinstance(user, User)
    assert user.id == 2
    assert user.name == "Test User Two"

def test_find_by_id_not_found(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test that finding a non-existent user by ID returns None."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    user = user_repository.find_by_id(99)
    
    assert user is None

def test_find_by_email(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test finding a user by email."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    user = user_repository.find_by_email("test1@example.com")
    
    assert user is not None
    assert user.id == 1

def test_add_user(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test adding a new user."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    new_user = User(
        id=3,
        name="New User",
        email="new@example.com",
        password="new_password", # Will be hashed by Pydantic model
        is_active=True,
        gender="other"
    )
    
    user_repository.add(new_user)
    
    mock_encryption_manager.encrypt_data.assert_called_once()
    mock_file_manager.write_file.assert_called_once()
    
    # Check the data that was passed to the encryption service
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_str = args[0]
    encrypted_payload_dict = json.loads(encrypted_payload_str)
    
    assert len(encrypted_payload_dict["users"]) == 3
    assert encrypted_payload_dict["users"][-1]["id"] == 3
    assert encrypted_payload_dict["users"][-1]["name"] == "New User"

def test_update_user(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test updating an existing user."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    updated_user = User(
        id=1,
        name="Updated Name",
        email="test1@example.com",
        password="hashed_password1",
        is_active=False,
        gender="male",
        bio="Updated bio."
    )
    
    result = user_repository.update(updated_user)
    
    assert result is not None
    assert result.name == "Updated Name"
    assert result.is_active is False
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert encrypted_payload_dict["users"][0]["name"] == "Updated Name"
    assert encrypted_payload_dict["users"][0]["is_active"] is False

def test_delete_user(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    """Test deleting a user."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    result = user_repository.delete(1)
    
    assert result is True
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert len(encrypted_payload_dict["users"]) == 1
    assert encrypted_payload_dict["users"][0]["id"] == 2
