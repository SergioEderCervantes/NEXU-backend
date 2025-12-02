from flask_socketio import SocketIO
from app.config.settings import Config
# Create the SocketIO instance here to avoid circular imports
socketio = SocketIO(cors_allowed_origins=Config.ALLOWED_ORIGINS)
