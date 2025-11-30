from typing import List, Optional
from jsonpath_ng.ext import parse
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

    def find_chat_by_users(self, user_id_1: str, user_id_2: str) -> Optional[Chat]:
        """
        Finds a chat by the two user IDs involved.

        Args:
            user_id_1 (str): The ID of the first user.
            user_id_2 (str): The ID of the second user.

        Returns:
            Optional[Chat]: The found chat, or None if no chat exists between the two users.
        """
        sorted_users = sorted([user_id_1, user_id_2])
        chat_id = f"{sorted_users[0]}-{sorted_users[1]}"
        return self.find_by_id(chat_id)

    def find_all_by_user(self, user_id: str) -> List[Chat]:
        """
        Finds all chats where the given user is a participant (either user_a or user_b).

        Args:
            user_id (str): The ID of the user to find chats for.

        Returns:
            List[Chat]: A list of chats involving the user.
        """
        data = self._get_data()
        # Correct JSONPath query using the union operator `|` to combine two separate filters.
        query = (f'$.{self.entity_name}[?(@.user_a == "{user_id}")] | '
                 f'$.{self.entity_name}[?(@.user_b == "{user_id}")]')
        jsonpath_expression = parse(query)
        matches = jsonpath_expression.find(data)
        
        # The union can produce duplicates if a user somehow chats with themselves.
        # We can remove duplicates by checking IDs.
        unique_matches = {match.value['id']: match.value for match in matches}.values()
        
        return [self._to_entity(value) for value in unique_matches]
