
from app.domain.entities import User
from app.extensions import socketio
from flask_socketio import disconnect, emit
from flask import session
from app.middleware.auth import socket_token_required
from app.application.ChatService import chat_service


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
    
    # Store user_id in the session for this connection
    session['user_id'] = user.id
    chat_service.manage_connection(user.id)


@socketio.on("disconnect")
def on_disconnect():
    """
    Handles user disconnection.
    Retrieves the user_id from the session to update their status.
    """
    user_id = session.get('user_id')
    chat_service.manage_disconnection(user_id)

    
@socketio.event
def start_chat(data):
    user_a_id = session.get('user_id')
    user_b_id = data['target_id']
    msg = data['content']
    if not user_a_id:
        emit("client_error", {"msg": "usuario no autenticado"})
        disconnect()
        return
    if not user_b_id or msg:
        emit("client_error", {"msg": "El id del usuario b y el primer mensaje son requeridos"})
    
    chat_service.start_chat(user_a_id, user_b_id, msg)


@socketio.event
def join_chat(data):
    """
    Allows a user to join a specific chat room after authentication.
    The user must be a participant in the chat.
    """
    user_id = session.get('user_id')
    chat_id = data.get('chat_id')

    if not user_id:
        emit("client_error", {"msg": "usuario no autenticado"})
        disconnect()
        return
    if not chat_id:
        emit("client_error", {"msg": "El id del chat es requerido"})

    chat_service.accept_chat(user_id, chat_id)

@socketio.event
def dm(data):
    user_id = session.get('user_id')
    chat_id = data.get('target_id')
    content = data.get('content')
    if not user_id:
        emit("client_error", {"msg": "usuario no autenticado"})
        disconnect()
        return
    if not chat_id or not content:
        emit("client_error", {"msg": "El id del chat y el mensaje son requeridos"})
        return
    
    chat_service.send_dm(user_id,chat_id, content)