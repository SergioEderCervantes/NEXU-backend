from app.repository.user_repository import UserRepository
from app.repository.chat_repository import ChatRepository
from app.repository.message_repository import MessageRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.application.UserService import UserService
from app.domain.entities import Chat, Message
from flask_socketio import join_room, emit, send
from app.extensions import socketio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, userRepository: UserRepository, chatRepository: ChatRepository, messageRepository: MessageRepository, user_service: UserService) -> None:
        self.user_repository = userRepository
        self.chat_repository = chatRepository
        self.message_repository = messageRepository
        self.user_service = user_service
        
    def manage_connection(self, user_id: str):
        # Each user joins a room named after their own user_id.
        # This makes it easy to send messages directly to a specific user.
        join_room(user_id)
        
        # Setting up online the user
        self.user_service.set_user_status(user_id, True)
        
        # Notifing a successful connection:
        send("Connected to server successfully and joined personal room.")
        # TODO: aqui se debe de hacer un query para ver si tiene nuevos mensajes, si si, mandarselos
    
    
    def manage_disconnection(self, user_id: str | None):
        if user_id:
            logger.info(f"User with ID {user_id} is disconnecting...")
            # Setting offline the user
            self.user_service.set_user_status(user_id, False)
        else:
            logger.info("An anonymous user is disconnecting.")
        
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
    
    def accept_chat(self, user_id, chat_id):
        chat = self.chat_repository.find_by_id(chat_id)

        if not chat:
            emit("server_error", {"msg": "El chat no fue encontrado"}, to=user_id)
            logger.warning(f"User {user_id} attempted to join non-existent chat {chat_id}.")
            return

        # Check if the user is a participant in this chat
        if user_id == chat.user_a or user_id == chat.user_b:
            join_room(chat_id)
            emit(f"Joined chat room: {chat_id}", to=user_id) # type: ignore
            logger.info(f"User {user_id} joined chat room {chat_id}")
            
            # Optionally, send past messages to the user - this would involve MessageRepository
        else:
            emit("client_error", {"msg": "You are not a participant in this chat."}, to=user_id)
            logger.warning(f"User {user_id} attempted to join chat {chat_id} without being a participant.")
            
            
    def send_dm(self, user_id, chat_id, content):
        chat = self.chat_repository.find_by_id(chat_id)

        if not chat:
            emit("server_error", {"msg": "El chat no fue encontrado"}, to=user_id)
            logger.warning(f"User {user_id} attempted to join non-existent chat {chat_id}.")
            return
        emit("dm",{
            "chat_id": chat_id,
            "sender": user_id,
            "content": content
        }, to=chat_id)

# Initialize dependencies for the ChatService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
chat_repository = ChatRepository(file_manager, encryption_manager)
message_repository = MessageRepository(file_manager, encryption_manager)
user_service = UserService(user_repository)

chat_service = ChatService(user_repository, chat_repository, message_repository, user_service)