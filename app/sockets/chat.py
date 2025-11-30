
from app.domain.entities import User
from app.extensions import socketio
from flask_socketio import disconnect, send, join_room
from flask import request, session
from app.middleware.auth import socket_token_required
from app.application.UserService import user_service
from app.repository.chat_repository import ChatRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
import logging

logger = logging.getLogger('app')

# Instantiate repositories globally for access within socket handlers
file_manager = FileManager()
encryption_manager = EncryptionManager()
chat_repository = ChatRepository(file_manager, encryption_manager)

@socketio.on("connect")
@socket_token_required
def on_connect(user:User, auth):
    """
    Handles new WebSocket connections, authenticates them, and adds them to a personal room.
    A connection is rejected if the token is invalid or missing.
    """
    if not user:
        # Returning False rejects the connection
        return False
    
    logger.info(f"User validated via socket: {user.email} (ID: {user.id})")
    
    # Store user_id in the session for this connection
    session['user_id'] = user.id
    
    # Each user joins a room named after their own user_id.
    # This makes it easy to send messages directly to a specific user.
    join_room(user.id)
    
    # Setting up online the user
    user_service.set_user_status(user.id, True)
    
    # Notifing a successful connection:
    send("Connected to server successfully and joined personal room.")
    # TODO: aqui se debe de hacer un query para ver si tiene nuevos mensajes, si si, mandarselos


@socketio.on("disconnect")
def on_disconnect():
    """
    Handles user disconnection.
    Retrieves the user_id from the session to update their status.
    """
    user_id = session.get('user_id')
    if user_id:
        logger.info(f"User with ID {user_id} is disconnecting...")
        # Setting offline the user
        user_service.set_user_status(user_id, False)
    else:
        logger.info("An anonymous user is disconnecting.")

    
@socketio.event
def start_chat(data):
   logger.debug(f"Si llegó el mensaje: {data["msg"]}")
   
   send("Mensaje recibido en el servidor")

@socketio.on('join_chat')
def on_join_chat(data):
    """
    Allows a user to join a specific chat room after authentication.
    The user must be a participant in the chat.
    """
    user_id = session.get('user_id')
    chat_id = data.get('chat_id')

    if not user_id:
        # User not authenticated for this session, disconnect or send error
        disconnect()
        return

    if not chat_id:
        send("Error: chat_id missing.", to=user_id) 
        return

    chat = chat_repository.find_by_id(chat_id)

    if not chat:
        send("Error: Chat not found.", to=user_id)
        logger.warning(f"User {user_id} attempted to join non-existent chat {chat_id}.")
        return

    # Check if the user is a participant in this chat
    if user_id == chat.user_a or user_id == chat.user_b:
        join_room(chat_id)
        send(f"Joined chat room: {chat_id}", to=request.sid) # type: ignore
        logger.info(f"User {user_id} joined chat room {chat_id}")
        
        # Optionally, send past messages to the user - this would involve MessageRepository
    else:
        send("Error: You are not a participant in this chat.", to=request.sid) # type: ignore
        logger.warning(f"User {user_id} attempted to join chat {chat_id} without being a participant.")
