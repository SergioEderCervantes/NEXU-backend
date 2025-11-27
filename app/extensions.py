from flask_socketio import SocketIO

# Create the SocketIO instance here to avoid circular imports
socketio = SocketIO(cors_allowed_origins="*")
