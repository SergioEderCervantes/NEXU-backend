import functools
from flask_socketio import disconnect
import jwt
from flask import request, jsonify, g
from app.config.settings import Config
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
import logging

logger = logging.getLogger('app')


def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info("Iniciando tarea de validacion de token")
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            logger.warning("Error: no se pudo extraer el token del request")
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            logger.info("Decodificando el JWT")
            
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]) # type: ignore
            user_id = payload['sub']
            logger.info(f"JWT decodificado, id del user: {user_id}")
            # user_id = int(user_id) # Removed int cast

            # This is not ideal as it creates a new instance every time.
            # In a real app, you would use a dependency injection system (like Flask-Injector)
            # or a singleton pattern to manage the repository instance.
            file_manager = FileManager()
            encryption_manager = EncryptionManager()
            user_repository = UserRepository(file_manager, encryption_manager)
            
            current_user = user_repository.find_by_id(user_id)
            if not current_user:
                return jsonify({'error': 'User not found.'}), 401
            
            g.current_user = current_user

        except jwt.ExpiredSignatureError:
            logger.warning("Token sent has expired!")
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token sent is invalido: {e}")
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            logger.warning(f'An unexpected error occurred during JWT decodification: {str(e)}')
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

        return f(*args, **kwargs)
    return decorated_function


def socket_token_required(f):
    """
    Decorator that authenticates a user from the socket connection auth data
    and passes the user object to the decorated function.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            logger.info("Iniciando validación de token para WebSocket")
            token = None
            
            # Try to get token from different sources
            # 1. From extraHeaders (HTTP_AUTHORIZATION in environ)
            if 'HTTP_AUTHORIZATION' in request.environ:
                auth_header = request.environ['HTTP_AUTHORIZATION']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    logger.info("Token extraído de HTTP_AUTHORIZATION")
            
            # 2. From auth parameter (if frontend sends it via socket.io auth)
            if not token and len(args) > 0 and isinstance(args[0], dict):
                auth_data = args[0]
                if 'token' in auth_data:
                    token = auth_data['token']
                    logger.info("Token extraído de auth.token")
                elif 'Authorization' in auth_data:
                    auth_val = auth_data['Authorization']
                    if auth_val.startswith('Bearer '):
                        token = auth_val.split(' ')[1]
                        logger.info("Token extraído de auth.Authorization")

            if not token:
                logger.warning("Token de WebSocket no encontrado en headers ni en auth")
                disconnect()
                return False

            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])  # type: ignore
            user_id = payload["sub"]
            logger.info(f"JWT decodificado para WebSocket, id del user: {user_id}")

            file_manager = FileManager()
            encryption_manager = EncryptionManager()
            user_repository = UserRepository(file_manager, encryption_manager)

            current_user = user_repository.find_by_id(user_id)
            if not current_user:
                logger.warning(f"Usuario no encontrado: {user_id}")
                disconnect()
                return False

            return f(current_user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            logger.warning("Token del WebSocket ha expirado")
            disconnect()
            return False
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token del WebSocket es inválido: {e}")
            disconnect()
            return False
        except Exception as e:
            logger.error(f"Error inesperado durante validación de WebSocket: {str(e)}", exc_info=True)
            disconnect()
            return False
    return decorated_function
