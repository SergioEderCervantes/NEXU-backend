from app.domain.entities import User
from app.extensions import socketio
from flask_socketio import disconnect, emit
from flask import session
from app.middleware.auth import socket_token_required
from app.application.ChatService import chat_service


@socketio.on("connect")
@socket_token_required
def on_connect(user: User, auth):
    """
    Handles new WebSocket connections, authenticates them, and adds them to a personal room.
    A connection is rejected if the token is invalid or missing.
    """
    if not user:
        # Returning False rejects the connection
        return False

    # Store user_id in the session for this connection
    session["user_id"] = user.id
    chat_service.manage_connection(user.id)


@socketio.on("disconnect")
def on_disconnect():
    """
    Handles user disconnection.
    Retrieves the user_id from the session to update their status.
    """
    user_id = session.get("user_id")
    chat_service.manage_disconnection(user_id)


@socketio.event
def start_chat(data):
    """
    Handles the initiation of a new chat between two users.
    Requires the target user's ID and the first message content.
    """
    user_a_id = session.get("user_id")
    user_b_id = data.get("target_id")
    msg = data.get("content")
    if not user_a_id:
        emit("client_error", {"msg": "User not authenticated"})
        disconnect()
        return
    if not user_b_id or not msg:
        emit(
            "client_error",
            {"msg": "Target user ID and first message are required"},
        )
        return

    chat_service.manage_start_chat(user_a_id, user_b_id, msg)


@socketio.event
def dm(data):
    """
    Handles direct messages sent within an existing chat.
    Requires the chat ID and the message content.
    """
    user_id = session.get("user_id")
    chat_id = data.get("target_id")
    content = data.get("content")
    if not user_id:
        emit("client_error", {"msg": "User not authenticated"})
        disconnect()
        return
    if not chat_id or not content:
        emit("client_error", {"msg": "Chat ID and message content are required"})
        return

    chat_service.manage_dm(user_id, chat_id, content)
