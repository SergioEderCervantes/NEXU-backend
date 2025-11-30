from app.domain.entities import Chat, DbFile
from app.repository.base_repository import BaseRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

class ChatRepository(BaseRepository[Chat]):
    """
    ChatRepository is a concrete implementation of BaseRepository specifically for Chat entities.
    It handles CRUD operations for Chat objects, leveraging the generic functionality
    provided by BaseRepository.
    """
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager):
        """
        Initializes the ChatRepository.

        Args:
            file_manager (FileManager): Service to handle file read/write operations.
            encryption_manager (EncryptionManager): Service to handle data encryption/decryption.
        """
        super().__init__(file_manager, encryption_manager, DbFile.CHATS, 'chats')

    def _to_entity(self, item: dict) -> Chat:
        """
        Converts a dictionary representation of a chat into a Chat domain entity object.

        Args:
            item (dict): A dictionary containing chat data.

        Returns:
            Chat: A Chat domain entity.
        """
        return Chat(**item)
