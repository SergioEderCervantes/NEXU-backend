import pytest
import json
from unittest.mock import MagicMock
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import User, DbFile

@pytest.fixture
def mock_file_manager():
    return MagicMock(spec=FileManager)

@pytest.fixture
def mock_encryption_manager():
    return MagicMock(spec=EncryptionManager)

@pytest.fixture
def user_repository(mock_file_manager, mock_encryption_manager):
    return UserRepository(mock_file_manager, mock_encryption_manager)

@pytest.fixture
def sample_users_data():
    return {
        "usuarios": [
            {
                "id": 1,
                "nombre_usuario": "testuser1",
                "correo_electronico": "test1@example.com",
                "contrasena_hash": "hash1",
                "nombre_completo": "Test User One",
                "biografia": "Bio 1",
                "habilidades": [],
                "reputacion": 10,
                "tags": []
            },
            {
                "id": 2,
                "nombre_usuario": "testuser2",
                "correo_electronico": "test2@example.com",
                "contrasena_hash": "hash2",
                "nombre_completo": "Test User Two",
                "biografia": "Bio 2",
                "habilidades": [1, 2],
                "reputacion": 20,
                "tags": [3]
            }
        ]
    }

def setup_mocks(mock_file_manager, mock_encryption_manager, data):
    """Helper function to set up mock return values."""
    json_data = json.dumps(data)
    encrypted_data = b'encrypted_data'
    
    mock_file_manager.read_file.return_value = encrypted_data
    mock_encryption_manager.decrypt_data.return_value = json_data
    mock_encryption_manager.encrypt_data.return_value = encrypted_data

def test_find_all(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    users = user_repository.find_all()
    
    assert len(users) == 2
    assert isinstance(users[0], User)
    assert users[0].id == 1
    assert users[1].nombre_usuario == "testuser2"
    mock_file_manager.read_file.assert_called_once_with(DbFile.USERS)
    mock_encryption_manager.decrypt_data.assert_called_once()

def test_find_by_id(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    user = user_repository.find_by_id(2)
    
    assert user is not None
    assert isinstance(user, User)
    assert user.id == 2
    assert user.nombre_completo == "Test User Two"

def test_find_by_id_not_found(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    user = user_repository.find_by_id(99)
    
    assert user is None

def test_find_by_username(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    user = user_repository.find_by_username("testuser1")
    
    assert user is not None
    assert user.id == 1

def test_add_user(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    new_user = User(
        id=3,
        nombre_usuario="newuser",
        correo_electronico="new@example.com",
        contrasena_hash="new_hash",
        nombre_completo="New User"
    )
    
    user_repository.add(new_user)
    
    # Verify that the data was encrypted and written
    mock_encryption_manager.encrypt_data.assert_called_once()
    mock_file_manager.write_file.assert_called_once()
    
    # Check the data that was passed to the encryption service
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_str = args[0]
    encrypted_payload_dict = json.loads(encrypted_payload_str)
    
    assert len(encrypted_payload_dict["usuarios"]) == 3
    assert encrypted_payload_dict["usuarios"][-1]["id"] == 3

def test_update_user(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    updated_user = User(
        id=1,
        nombre_usuario="updated_user",
        correo_electronico="test1@example.com",
        contrasena_hash="hash1",
        nombre_completo="Updated Name",
        biografia="Updated Bio"
    )
    
    result = user_repository.update(updated_user)
    
    assert result is not None
    assert result.nombre_usuario == "updated_user"
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert encrypted_payload_dict["usuarios"][0]["nombre_usuario"] == "updated_user"
    assert encrypted_payload_dict["usuarios"][0]["nombre_completo"] == "Updated Name"

def test_delete_user(user_repository, mock_file_manager, mock_encryption_manager, sample_users_data):
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_users_data)
    
    result = user_repository.delete(1)
    
    assert result is True
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert len(encrypted_payload_dict["usuarios"]) == 1
    assert encrypted_payload_dict["usuarios"][0]["id"] == 2
