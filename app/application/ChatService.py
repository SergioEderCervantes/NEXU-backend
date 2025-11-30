from app.repository.user_repository import UserRepository
from app.repository.chat_repository import ChatRepository
from app.repository.message_repository import MessageRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import Chat, Message
from flask_socketio import join_room, emit
from app.extensions import socketio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, userRepository: UserRepository, chatRepository: ChatRepository, messageRepository: MessageRepository) -> None:
        self.user_repository = userRepository
        self.chat_repository = chatRepository
        self.message_repository = messageRepository
        
    def start_chat(self, user_a_id: str, user_b_id:str, first_msg_content:str):
        user_a = self.user_repository.find_by_id(user_a_id)
        user_b = self.user_repository.find_by_id(user_b_id)
        if not user_b or not user_a:
            # El usuario b no se encontro
            return

        # Check if a chat already exists between these two users
        # For now, let's assume it doesn't exist and create a new one.
        # This part should be more robust in a real application, checking for existing chats
        # For example, you might want to find_by_attribute('user_a', user_a_id) and ('user_b', user_b_id)
        # or vice versa. This will require a custom method in ChatRepository or
        # iterating through all chats.

        new_chat = Chat(user_a=user_a_id, user_b=user_b_id)
        self.chat_repository.add(new_chat) # Save the new chat
        logger.info(f"New chat {new_chat.id} created between {user_a.id} and {user_b.id}")

        # User A joins the chat room
        join_room(new_chat.id)
        logger.info(f"User {user_a.id} joined chat room {new_chat.id}")

        # If user_b is active, join him to the chat
            

        # Notify User B by emitting to their personal room (user_b.id)
        # user_b.id is the room name for user B's active connections
        socketio.emit('chat_invitation', 
             {'chat_id': new_chat.id, 
              'from_user_id': user_a.id,
              'from_user_name': user_a.name,
              'first_message': first_msg_content},
             to=user_b.id)
        logger.info(f"Sent chat invitation to user {user_b.id} for chat {new_chat.id}")


        # Create and save the first message
        first_message = Message(
            conversation_id=new_chat.id,
            sender_id=user_a.id,
            content=first_msg_content,
            timestamp=datetime.now(),
            delivered=False # Will be delivered when user B joins and confirms receipt
        )
        self.message_repository.add(first_message)
        logger.info(f"First message for chat {new_chat.id} saved.")

# Initialize dependencies for the ChatService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
chat_repository = ChatRepository(file_manager, encryption_manager)
message_repository = MessageRepository(file_manager, encryption_manager)

chat_service = ChatService(user_repository, chat_repository, message_repository)