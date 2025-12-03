from app.repository.user_repository import UserRepository
from app.repository.chat_repository import ChatRepository
from app.repository.message_repository import MessageRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.application.UserService import UserService
from app.domain.entities import Chat, Message, User
from flask_socketio import join_room, emit, send
from app.extensions import socketio
from datetime import datetime
import logging

logger = logging.getLogger('app')


class ChatService:
    """
    Manages chat-related functionalities, including user connections,
    messaging, and chat retrieval.
    """
    def __init__(
        self,
        userRepository: UserRepository,
        chatRepository: ChatRepository,
        messageRepository: MessageRepository,
        user_service: UserService,
    ) -> None:
        """
        Initializes the ChatService with necessary repositories and services.

        Args:
            userRepository: The repository for user data.
            chatRepository: The repository for chat data.
            messageRepository: The repository for message data.
            user_service: The service for user-related operations.
        """
        self.user_repository = userRepository
        self.chat_repository = chatRepository
        self.message_repository = messageRepository
        self.user_service = user_service

    # ----------- Main socket event handlers ------------------
    def manage_connection(self, user_id: str):
        """
        Manages a new user connection by joining them to a personal room
        and updating their status to 'online'.

        Args:
            user_id: The ID of the user connecting.
        """
        # Each user joins a room named after their own user_id.
        join_room(user_id)

        # Setting up online the user
        self.user_service.set_user_status(user_id, True)
        logger.info(f"Setting user with id {user_id} to online")

        # Notifing a successful connection:
        send("Connected to server successfully and joined personal room.")

    def manage_disconnection(self, user_id: str | None):
        """
        Manages a user disconnection by updating their status to 'offline'.

        Args:
            user_id: The ID of the user disconnecting. Can be None if the
            user was not authenticated.
        """
        if user_id:
            logger.info(f"User with ID {user_id} is disconnecting...")
            # Setting offline the user
            self.user_service.set_user_status(user_id, False)
        else:
            logger.info("An anonymous user is disconnecting.")

    def manage_start_chat(self, user_a_id: str, user_b_id: str, first_msg_content: str):
        """
        Manages the first message sent between two users, creating a new
        chat if one doesn't already exist.

        Args:
            user_a_id: The ID of the user initiating the chat.
            user_b_id: The ID of the user receiving the first message.
            first_msg_content: The content of the first message.
        """
        user_a = self.user_repository.find_by_id(user_a_id)
        user_b = self.user_repository.find_by_id(user_b_id)
        if not user_a or not user_b:
            # One of the users was not found
            logger.warning(
                f"Attempted to start chat but user not found. user_a: {user_a_id}, user_b: {user_b_id}"
            )
            return

        # Check if a chat already exists between these two users
        chat = self.chat_repository.find_chat_by_users(user_a_id, user_b_id)

        if not chat:
            # Chat does not exist, create a new one
            chat = Chat(user_a=user_a_id, user_b=user_b_id)
            self.chat_repository.add(chat)
            logger.info(
                f"New chat {chat.id} created between {user_a.id} and {user_b.id}"
            )

        # Create and save the first message
        first_message = Message(
            conversation_id=chat.id,
            sender_id=user_a.id,
            content=first_msg_content,
            timestamp=datetime.now(),
            delivered=False,
        )
        self.message_repository.add(first_message)
        logger.info(f"First message for chat {chat.id} saved.")
        # Notifying the reciever
        self._send_notification(user_a, chat, user_b, first_message)


    def manage_dm(self, user_id: str, chat_id: str, content: str):
        """
        Manages a direct message sent within an existing chat.

        Args:
            user_id: The ID of the user sending the message.
            chat_id: The ID of the chat the message belongs to.
            content: The content of the message.
        """
        chat = self.chat_repository.find_by_id(chat_id)

        if not chat:
            emit("server_error", {"msg": "El chat no fue encontrado"}, to=user_id)
            logger.error(
                f"User {user_id} attempted to join non-existent chat {chat_id}."
            )
            return
        # Update the last_message_at timestamp of the chat
        chat.last_message_at = datetime.now()
        self.chat_repository.update(chat)
        # Create the new message
        new_message = Message(
            conversation_id=chat_id, sender_id=user_id, content=content, delivered=False
        )
        self.message_repository.add(new_message)
        sender = self.user_repository.find_by_id(user_id)
        reciever = self.user_repository.find_by_id(
            chat.user_a if chat.user_a != user_id else chat.user_b
        )
        if not sender or not reciever:
            # One of the users was not found
            logger.warning(
                "Attempted to send dm but users not found"
            )
            return
        self._send_notification(sender, chat, reciever, new_message)


    # ----------- Helper functions ------------------
    
    def _send_notification(
        self, sender: User, chat: Chat, reciever: User, message: Message
    ):
        """
        Sends a real-time notification to a user about a new message.

        Args:
            sender: The user who sent the message.
            chat: The chat the message belongs to.
            reciever: The user who should receive the notification.
            message: The message that was sent.
        """
        logger.info(f"Sending dm to {reciever.name} from: {sender.name}")
        socketio.emit(
            "new_notification",
            {
                "chat_id": chat.id,
                "sender_id": sender.id,
                "sender_name": sender.name,
                "message": message.content,
            },
            to=reciever.id,
        )


    def get_chats_for_user(self, user_id: str) -> list:
        """
        Retrieves all chats for a given user, along with details about the other
        participant and the number of unread messages.
        
        Args:
            user_id: The ID of the user whose chats are to be retrieved.

        Returns:
            A list of chats, sorted by the most recent message.
        """
        logger.debug(f"Intentando encontrar chats del user: {user_id}")
        chats = self.chat_repository.find_all_by_user(user_id)
        logger.debug(f"Chats del userid: {len(chats)}")
        response = []

        for chat in chats:
            other_user_id = chat.user_b if chat.user_a == user_id else chat.user_a
            other_user = self.user_repository.find_by_id(other_user_id)

            if not other_user:
                logger.warning(
                    f"Could not find other user with id {other_user_id} for chat {chat.id}"
                )
                continue

            unread_count = self.message_repository.count_unread_by_chat(
                chat.id, user_id
            )
            
            last_message = self.message_repository.find_last_by_conversation_id(chat.id)
            
            last_message_data = None
            if last_message:
                last_message_data = {
                    "content": last_message.content,
                    "timestamp": last_message.timestamp.isoformat()
                }

            response.append(
                {
                    "id": chat.id,
                    "last_message_at": chat.last_message_at.isoformat(),
                    "other_user": {
                        "id": other_user.id,
                        "name": other_user.name,
                        "is_active": other_user.is_active,
                    },
                    "unread_messages": unread_count,
                    "last_message": last_message_data,
                }
            )

        # Sort chats by last message time, newest first
        response.sort(key=lambda x: x["last_message_at"], reverse=True)

        return response

    def load_chat_msgs(self, chat:Chat, user:User | str):
        messages = self.message_repository.find_by_conversation_id(chat.id)
        return messages
    
    def get_all(self):
        chats = self.chat_repository.find_all()
        return chats

# Initialize dependencies for the ChatService
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)
chat_repository = ChatRepository(file_manager, encryption_manager)
message_repository = MessageRepository(file_manager, encryption_manager)
user_service = UserService(user_repository)

chat_service = ChatService(
    user_repository, chat_repository, message_repository, user_service
)
