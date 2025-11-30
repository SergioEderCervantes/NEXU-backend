
from app.domain.entities import User
from app.extensions import socketio
from flask_socketio import disconnect, send
from app.middleware.auth import socket_token_required
from app.application.UserService import user_service
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
    user_service.set_user_status(user.id, True)
    # Notifing a successful connection:
    send("Connected to server successfully")
    # TODO: aqui se debe de hacer un query para ver si tiene nuevos mensajes, si si, mandarselos




@socketio.on("disconnect")
@socket_token_required
def on_disconnect(user:User):
    if not user:
        return False
    logger.info(f"Usuario {user.email} se esta desconectando de la aplicacion...")
    # Setting offline the user
    user_service.set_user_status(user.id, False)
    disconnect()
    
    
@socketio.event
def start_chat(data):
   logger.debug(f"Si llegó el mensaje: {data["msg"]}")
   
   send("Mensaje recibido en el servidor")
