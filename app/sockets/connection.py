from app.extensions import socketio
from app.middleware.auth import socket_token_required
from flask import g
import logging
logger = logging.getLogger('app')

@socketio.on("connect")
@socket_token_required
def on_connect(auth):
    logger.debug("User validated vía socket:", g.current_user)
