from typing import List
from app.domain.entities import Message, DbFile
from app.repository.base_repository import BaseRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from jsonpath_ng.ext import parse

class MessageRepository(BaseRepository[Message]):
    """
    MessageRepository is a concrete implementation of BaseRepository specifically for Message entities.
    It handles CRUD operations for Message objects and provides custom methods for message retrieval.
    """
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager):
        """
        Initializes the MessageRepository.

        Args:
            file_manager (FileManager): Service to handle file read/write operations.
            encryption_manager (EncryptionManager): Service to handle data encryption/decryption.
        """
        super().__init__(file_manager, encryption_manager, DbFile.MESSAGES, 'messages')

    def _to_entity(self, item: dict) -> Message:
        """
        Converts a dictionary representation of a message into a Message domain entity object.

        Args:
            item (dict): A dictionary containing message data.

        Returns:
            Message: A Message domain entity.
        """
        return Message(**item)

    def find_many_by_attribute(self, attribute: str, value: str) -> List[Message]:
        """
        Finds all entities with a specific attribute and its value.

        Args:
            attribute (str): The name of the attribute to search by.
            value (str): The value of the attribute to match.

        Returns:
            List[Message]: A list of found entities.
        """
        data = self._get_data()
        query_value = f'"{value}"' if isinstance(value, str) else value
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.{attribute} == {query_value})]')
        matches = jsonpath_expression.find(data)
        return [self._to_entity(match.value) for match in matches]

    def find_by_conversation_id(self, conversation_id: str) -> List[Message]:
        """
        Finds all messages in a conversation, sorted by timestamp.

        Args:
            conversation_id (str): The ID of the conversation.

        Returns:
            List[Message]: A list of messages in the conversation.
        """
        messages = self.find_many_by_attribute('conversation_id', conversation_id)
        # Sort messages by timestamp
        messages.sort(key=lambda x: x.timestamp)
        return messages

    def count_unread_by_chat(self, chat_id: str, user_id: str) -> int:
        """
        Counts unread messages in a specific chat for a given user.
        Unread messages are those not sent by the user and marked as not delivered.

        Args:
            chat_id (str): The ID of the chat (conversation).
            user_id (str): The ID of the user for whom to count unread messages.

        Returns:
            int: The number of unread messages.
        """
        data = self._get_data()
        # Correct JSONPath using `&` for AND logic within a filter expression.
        query = (f'$.{self.entity_name}[?(@.conversation_id == "{chat_id}" & '
                 f'@.sender_id != "{user_id}" & @.delivered == false)]')
        jsonpath_expression = parse(query)
        matches = jsonpath_expression.find(data)
        return len(matches)
