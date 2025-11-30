import pytest
import json
from unittest.mock import MagicMock
from app.repository.message_repository import MessageRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import Message
from datetime import datetime, timedelta
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
def message_repository(mock_file_manager, mock_encryption_manager):
    """Fixture for MessageRepository with mocked dependencies."""
    return MessageRepository(mock_file_manager, mock_encryption_manager)

@pytest.fixture
def sample_messages_data():
    """Sample message data that mimics the structure in the JSON file."""
    conversation_id_1 = str(uuid.uuid4())
    now = datetime.now()
    return {
        "messages": [
            {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id_1,
                "sender_id": str(uuid.uuid4()),
                "content": "Hello!",
                "timestamp": (now - timedelta(minutes=10)).isoformat(),
                "delivered": True,
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": str(uuid.uuid4()), # Different conversation
                "sender_id": str(uuid.uuid4()),
                "content": "Another conversation.",
                "timestamp": now.isoformat(),
                "delivered": True,
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id_1,
                "sender_id": str(uuid.uuid4()),
                "content": "How are you?",
                "timestamp": (now - timedelta(minutes=5)).isoformat(),
                "delivered": False,
            }
        ]
    }

def setup_mocks(mock_file_manager, mock_encryption_manager, data):
    """Helper to configure mocks for reading data."""
    json_data = json.dumps(data, indent=4)
    encrypted_data = b'encrypted_data_mock'
    
    mock_file_manager.read_file.return_value = encrypted_data
    mock_encryption_manager.decrypt_data.return_value = json_data
    mock_encryption_manager.encrypt_data.return_value = b'new_encrypted_data'

# --- Repository Tests ---

def test_find_all(message_repository, mock_file_manager, mock_encryption_manager, sample_messages_data):
    """Test finding all messages."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_messages_data)
    
    messages = message_repository.find_all()
    
    assert len(messages) == 3
    assert isinstance(messages[0], Message)
    assert messages[0].id == sample_messages_data["messages"][0]["id"]

def test_find_by_id(message_repository, mock_file_manager, mock_encryption_manager, sample_messages_data):
    """Test finding a message by ID."""
    message_id_to_find = sample_messages_data["messages"][1]["id"]
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_messages_data)
    
    message = message_repository.find_by_id(message_id_to_find)
    
    assert message is not None
    assert isinstance(message, Message)
    assert message.id == message_id_to_find

def test_add_message(message_repository, mock_file_manager, mock_encryption_manager, sample_messages_data):
    """Test adding a new message."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_messages_data)
    
    new_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        sender_id=str(uuid.uuid4()),
        content="New message!",
        delivered=False
    )
    
    message_repository.add(new_message)
    
    mock_encryption_manager.encrypt_data.assert_called_once()
    mock_file_manager.write_file.assert_called_once()
    
    args, _ = mock_encryption_manager.encrypt_data.call_args
    encrypted_payload_dict = json.loads(args[0])
    
    assert len(encrypted_payload_dict["messages"]) == 4
    assert encrypted_payload_dict["messages"][-1]["id"] == new_message.id

def test_find_by_conversation_id(message_repository, mock_file_manager, mock_encryption_manager, sample_messages_data):
    """Test finding messages by conversation ID."""
    conversation_id = sample_messages_data["messages"][0]["conversation_id"]
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_messages_data)

    messages = message_repository.find_by_conversation_id(conversation_id)

    assert len(messages) == 2
    assert all(isinstance(m, Message) for m in messages)
    assert all(m.conversation_id == conversation_id for m in messages)
    # Test that messages are sorted by timestamp
    assert messages[0].timestamp < messages[1].timestamp
    assert messages[0].content == "Hello!"
    assert messages[1].content == "How are you?"

def test_find_by_conversation_id_not_found(message_repository, mock_file_manager, mock_encryption_manager, sample_messages_data):
    """Test finding messages for a conversation that has none."""
    setup_mocks(mock_file_manager, mock_encryption_manager, sample_messages_data)

    messages = message_repository.find_by_conversation_id(str(uuid.uuid4()))

    assert len(messages) == 0
