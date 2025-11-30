import pytest
import json
from unittest.mock import MagicMock
from app.repository.chat_repository import ChatRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import Chat, DbFile
from datetime import datetime
import uuid

@pytest.fixture
def mock_file_manager():
    """Mock for FileManager."""
    return MagicMock(spec=FileManager)

@pytest.fixture
def mock_encryption_manager():
    """Mock for EncryptionManager."""
    return MagicMock(spec=EncryptionManager)

@pytest.fixture
def chat_repository(mock_file_manager, mock_encryption_manager):
    """Fixture for ChatRepository with mocked dependencies."""
    return ChatRepository(mock_file_manager, mock_encryption_manager)

@pytest.fixture
def sample_chats_data():
    """Sample chat data that mimics the structure in the JSON file."""
    return {
        "chats": [
            {
                "id": str(uuid.uuid4()),
                "user_a": str(uuid.uuid4()),
                "user_b": str(uuid.uuid4()),
                "last_message_at": datetime.now().isoformat(),
            },
            {
                "id": str(uuid.uuid4()),
                "user_a": str(uuid.uuid4()),
                "user_b": str(uuid.uuid4()),
                "last_message_at": datetime.now().isoformat(),
            }
        ]
    }

@pytest.fixture
def sample_chat_for_user_lookup():
    """A specific chat for testing find_chat_by_users."""
    user_id_1 = "user-sorted-first-id"
    user_id_2 = "user-sorted-second-id"
    chat = Chat(user_a=user_id_1, user_b=user_id_2)
    return {
        "user_id_1": user_id_1,
        "user_id_2": user_id_2,
        "chat": chat,
        "data": {"chats": [chat.model_dump(mode='json')]}
    }


def setup_mocks(mock_file_manager, mock_encryption_manager, data):
    """Helper to configure mocks for reading data."""
    json_data = json.dumps(data, indent=4)
    encrypted_data = b'encrypted_data_mock'
    
    mock_file_manager.read_file.return_value = encrypted_data
    mock_encryption_manager.decrypt_data.return_value = json_data
    mock_encryption_manager.encrypt_data.return_value = b'new_encrypted_data'

# --- Repository Tests ---

def test_find_all(chat_repository, mock_file_manager, mock_encryption_manager, sample_chats_data):
    """Test finding all chats."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chats_data)
    
    chats = chat_repository.find_all()
    
    assert len(chats) == 2
    assert isinstance(chats[0], Chat)
    assert chats[0].id == sample_chats_data["chats"][0]["id"]
    mock_file_manager.read_file.assert_called_once_with(DbFile.CHATS)
    mock_encryption_manager.decrypt_data.assert_called_once_with(b'encrypted_data_mock')

def test_find_by_id(chat_repository, mock_file_manager, mock_encryption_manager, sample_chats_data):
    """Test finding a chat by ID."""
    chat_id_to_find = sample_chats_data["chats"][1]["id"]
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chats_data)
    
    chat = chat_repository.find_by_id(chat_id_to_find)
    
    assert chat is not None
    assert isinstance(chat, Chat)
    assert chat.id == chat_id_to_find

def test_find_by_id_not_found(chat_repository, mock_file_manager, mock_encryption_manager, sample_chats_data):
    """Test that finding a non-existent chat by ID returns None."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chats_data)
    
    chat = chat_repository.find_by_id(str(uuid.uuid4()))
    
    assert chat is None

def test_add_chat(chat_repository, mock_file_manager, mock_encryption_manager, sample_chats_data):
    """Test adding a new chat."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chats_data)
    
    new_chat = Chat(
        user_a=str(uuid.uuid4()),
        user_b=str(uuid.uuid4())
    )
    
    chat_repository.add(new_chat)
    
    mock_encryption_manager.encrypt_data.assert_called_once()
    mock_file_manager.write_file.assert_called_once()
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_str = args[0]
    encrypted_payload_dict = json.loads(encrypted_payload_str)
    
    assert len(encrypted_payload_dict["chats"]) == 3
    assert encrypted_payload_dict["chats"][-1]["id"] == new_chat.id

def test_update_chat(chat_repository, mock_file_manager, mock_encryption_manager, sample_chats_data):
    """Test updating an existing chat."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chats_data)
    
    chat_to_update = sample_chats_data["chats"][0]
    # Recreate the chat object from dict to ensure types are correct
    original_chat_obj = Chat(**chat_to_update)

    # Now create the updated version
    updated_chat = original_chat_obj.model_copy(update={"user_b": str(uuid.uuid4())})

    result = chat_repository.update(updated_chat)
    
    assert result is not None
    assert result.user_b == updated_chat.user_b
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert encrypted_payload_dict["chats"][0]["user_b"] == updated_chat.user_b

def test_delete_chat(chat_repository, mock_file_manager, mock_encryption_manager, sample_chats_data):
    """Test deleting a chat."""
    chat_id_to_delete = sample_chats_data["chats"][0]["id"]
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chats_data)
    
    result = chat_repository.delete(chat_id_to_delete)
    
    assert result is True
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert len(encrypted_payload_dict["chats"]) == 1
    assert encrypted_payload_dict["chats"][0]["id"] == sample_chats_data["chats"][1]["id"]

def test_find_chat_by_users_success_original_order(chat_repository, mock_file_manager, mock_encryption_manager, sample_chat_for_user_lookup):
    """Test finding a chat by user IDs when they are provided in the original sorted order."""
    user_id_1 = sample_chat_for_user_lookup["user_id_1"]
    user_id_2 = sample_chat_for_user_lookup["user_id_2"]
    expected_chat = sample_chat_for_user_lookup["chat"]
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chat_for_user_lookup["data"])

    found_chat = chat_repository.find_chat_by_users(user_id_1, user_id_2)
    assert found_chat is not None
    assert found_chat.id == expected_chat.id
    assert found_chat.user_a == expected_chat.user_a
    assert found_chat.user_b == expected_chat.user_b

def test_find_chat_by_users_success_reversed_order(chat_repository, mock_file_manager, mock_encryption_manager, sample_chat_for_user_lookup):
    """Test finding a chat by user IDs when they are provided in reversed order."""
    user_id_1 = sample_chat_for_user_lookup["user_id_1"]
    user_id_2 = sample_chat_for_user_lookup["user_id_2"]
    expected_chat = sample_chat_for_user_lookup["chat"]
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chat_for_user_lookup["data"])

    found_chat = chat_repository.find_chat_by_users(user_id_2, user_id_1)
    assert found_chat is not None
    assert found_chat.id == expected_chat.id
    assert found_chat.user_a == expected_chat.user_a
    assert found_chat.user_b == expected_chat.user_b

def test_find_chat_by_users_not_found(chat_repository, mock_file_manager, mock_encryption_manager, sample_chat_for_user_lookup):
    """Test that find_chat_by_users returns None if no chat exists for the given user IDs."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_chat_for_user_lookup["data"])

    not_found_chat = chat_repository.find_chat_by_users("non_existent_user_1", "non_existent_user_2")
    assert not_found_chat is None
