from flask import Flask
# TODO: Configurar APS para Scheduled tasks
from app.config.logger import setup_logging
from app.middleware.logging_middleware import log_request_time
from app.api import register_blueprints
import logging
from app.extensions import socketio
from app.config.settings import Config
from flask_cors import CORS

def create_app():
    """
    Creates and configures a Flask application instance, including blueprints
    and extensions.
    """
    logger = setup_logging(logging_level=logging.DEBUG)
    
    flask_app = Flask(__name__)
    flask_app.config['SECRET_KEY']= Config.FLASK_SECRET_KEY

    # Initialize CORS
    CORS(flask_app, resources={r"/*": {"origins": "*"}})
    
    # Set up middleware
    log_request_time(flask_app)
    
    # Register blueprints
    register_blueprints(flask_app)
    
    # Import socket handlers to register them
    import app.sockets.chat
    
    # Initialize Socket.IO with the app
    socketio.init_app(flask_app)
    
    logger.info("Flask application created and configured successfully.")
    
    return flask_app

if __name__ == "__main__":
    flask_app = create_app()
    socketio.run(flask_app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
