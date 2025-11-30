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
        
    def get_chats_for_user(self, user_id: str) -> list:
        """
        Retrieves all chats for a given user, along with details about the other
        participant and the number of unread messages.
        """
        chats = self.chat_repository.find_all_by_user(user_id)
        response = []

        for chat in chats:
            other_user_id = chat.user_b if chat.user_a == user_id else chat.user_a
            other_user = self.user_repository.find_by_id(other_user_id)
            
            if not other_user:
                logger.warning(f"Could not find other user with id {other_user_id} for chat {chat.id}")
                continue

            unread_count = self.message_repository.count_unread_by_chat(chat.id, user_id)
            
            response.append({
                "id": chat.id,
                "last_message_at": chat.last_message_at.isoformat(),
                "other_user": {
                    "id": other_user.id,
                    "name": other_user.name,
                    "is_active": other_user.is_active
                },
                "unread_messages": unread_count
            })
            
        # Sort chats by last message time, newest first
        response.sort(key=lambda x: x['last_message_at'], reverse=True)
        
        return response

    def start_chat(self, user_a_id: str, user_b_id:str, first_msg_content:str):
        user_a = self.user_repository.find_by_id(user_a_id)
        user_b = self.user_repository.find_by_id(user_b_id)
        if not user_a or not user_b:
            # One of the users was not found
            logger.warning(f"Attempted to start chat but user not found. user_a: {user_a_id}, user_b: {user_b_id}")
            return

        # Check if a chat already exists between these two users
        chat = self.chat_repository.find_chat_by_users(user_a_id, user_b_id)

        if chat:
            # Chat already exists, join the room and send the message
            logger.info(f"Joining existing chat {chat.id} between {user_a.id} and {user_b.id}")
            join_room(chat.id)
            logger.info(f"User {user_a.id} joined chat room {chat.id}")
            
            # Send the "first message" as a regular direct message since the chat is already established
            self.send_dm(user_a_id, chat.id, first_msg_content)

        else:
            # Chat does not exist, create a new one
            new_chat = Chat(user_a=user_a_id, user_b=user_b_id)
            self.chat_repository.add(new_chat) # Save the new chat
            chat = new_chat # Use the new chat object from here on
            logger.info(f"New chat {chat.id} created between {user_a.id} and {user_b.id}")

            # User A joins the new chat room
            join_room(chat.id)
            logger.info(f"User {user_a.id} joined chat room {chat.id}")

            # Notify User B by emitting to their personal room (user_b.id)
            socketio.emit('chat_invitation', 
                {'chat_id': chat.id, 
                'from_user_id': user_a.id,
                'from_user_name': user_a.name,
                'first_message': first_msg_content},
                to=user_b.id)
            logger.info(f"Sent chat invitation to user {user_b.id} for chat {chat.id}")

            # Create and save the first message
            first_message = Message(
                conversation_id=chat.id,
                sender_id=user_a.id,
                content=first_msg_content,
                timestamp=datetime.now(),
                delivered=False # Will be delivered when user B joins and confirms receipt
            )
            self.message_repository.add(first_message)
            logger.info(f"First message for chat {chat.id} saved.")
    
    def accept_chat(self, user_id, chat_id):
        """Esta funcion no es solo cuando la primera vez que se unen al chat, si no cada que el usuario quiera entrar a un chat,
        en este caso se une a la room del chat, se cargan todos los mensajes del chat y se settea como entregados si hay alguno que todavia este
        como no entregado"""
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
            # Aqui se van a cargar todos los chats
        else:
            emit("client_error", {"msg": "You are not a participant in this chat."}, to=user_id)
            logger.warning(f"User {user_id} attempted to join chat {chat_id} without being a participant.")
            
            
    def send_dm(self, user_id, chat_id, content):
        chat = self.chat_repository.find_by_id(chat_id)

        if not chat:
            emit("server_error", {"msg": "El chat no fue encontrado"}, to=user_id)
            logger.warning(f"User {user_id} attempted to join non-existent chat {chat_id}.")
            return
        # Actualizamos el last messsage at del chat
        chat.last_message_at = datetime.now()
        self.chat_repository.update(chat)
        # Creamos el mensaje
        new_message = Message(conversation_id=chat_id, sender_id=user_id, content=content, delivered=False)
        # verificamos que el user de destino este activo para mandar el mensaje, si no se pone como delivered False
        target_user = self.user_repository.find_by_id(chat.user_a if chat.user_a != user_id else chat.user_b)
        
        if not target_user:
            emit("server_error", {"msg": "usuario 2 del chat no encontrado"})
        elif target_user.is_active:
            # El usuario 2 esta online, se guarda como delivered
            new_message.delivered = True
        
        self.message_repository.add(new_message)
        
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