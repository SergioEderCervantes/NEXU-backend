from app.domain.entities import User
from app.extensions import socketio
from flask_socketio import disconnect
from app.middleware.auth import socket_token_required
import logging
logger = logging.getLogger('app')

@socketio.on("connect")
@socket_token_required
def on_connect(user:User, auth):
    """
    Handles new WebSocket connections and authenticates them.
    A connection is rejected if the token is invalid or missing.
    """
    if not user:
        # Returning False rejects the connection
        return False
    
    logger.info(f"User validated via socket: {user.email} (ID: {user.id})")
    # Setting up online the user
    user.is_active = True




@socketio.on("disconnect")
@socket_token_required
def on_disconnect(user:User):
    if not user:
        return False
    logger.info(f"Usuario {user.email} se esta desconectando de la aplicacion...")
    disconnect()
    # Setting offline the user
    user.is_active = False
    
    
    