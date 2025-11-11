from flask import Flask
from flask_socketio import SocketIO
# TODO: Configurar APS para Scheduled tasks
from app.config.logger import setup_logging
from app.middleware.logging_middleware import log_request_time
from app.api import register_blueprints
logger = setup_logging()
# TODO: Mover esta config a un settings.py
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    # Setteando el middleware
    log_request_time(app)

    # Registro de las blueprints
    register_blueprints(app)
    # Registro de scheduled tasks

    logger.info("Aplicacion Flask inicializada correctamente")
    return app


if __name__ == "__main__":
    app = create_app()
    socketio.init_app(app)
    socketio.run(app,host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
