from app.extensions import socketio
from app.middleware.auth import get_user_from_socket_header
from flask import g
import logging
logger = logging.getLogger('app')

@socketio.on("connect")
def on_connect():
    """
    Handles new WebSocket connections and authenticates them.
    A connection is rejected if the token is invalid or missing.
    """
    user = get_user_from_socket_header()
    if not user:
        # Returning False rejects the connection
        return False
    
    # Store the user in Flask's application context global `g`
    g.current_user = user
    logger.info(f"User validated via socket: {g.current_user.email} (ID: {g.current_user.id})")
    # You can add logic here to set user status to online, etc.

