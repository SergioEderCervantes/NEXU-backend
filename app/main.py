from flask import Flask
# TODO: Configurar APS para Scheduled tasks
from app.config.logger import setup_logging
from app.middleware.logging_middleware import log_request_time
from app.api import register_blueprints
import logging
from app.extensions import socketio # Import socketio from extensions

logger = setup_logging(logging_level=logging.DEBUG)

# Create the Flask app instance
flask_app:Flask = Flask(__name__)

# Setteando el middleware
log_request_time(flask_app)

# Registro de las blueprints
register_blueprints(flask_app)
# Registro de scheduled tasks

# Import socket handlers to register them
import app.sockets.connection

socketio.init_app(flask_app) 
# Initialize Socket.IO with the app

logger.info("Aplicacion Flask inicializada correctamente")

if __name__ == "__main__":
    socketio.run(flask_app,host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
