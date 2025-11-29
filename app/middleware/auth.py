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
            user_id = int(user_id)

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
    Decorator that authenticates a user from the socket connection headers
    and passes the user object to the decorated function.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            logger.info("Iniciando validación de token para WebSocket desde headers")
            token = None
            # During a Socket.IO connection, headers are in the WSGI environ dictionary
            if 'HTTP_AUTHORIZATION' in request.environ:
                auth_header = request.environ['HTTP_AUTHORIZATION']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            else:
                logger.debug(f"Asi se ve el request: {request}")

            if not token:
                logger.warning("Token de WebSocket no encontrado en los headers (Authorization: Bearer ...)")
                disconnect()
                return

            logger.info("Decodificando el JWT del WebSocket")
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])  # type: ignore
            user_id = int(payload["sub"])
            logger.info(f"JWT decodificado, id del user: {user_id}")

            file_manager = FileManager()
            encryption_manager = EncryptionManager()
            user_repository = UserRepository(file_manager, encryption_manager)

            current_user = user_repository.find_by_id(user_id)
            if not current_user:
                logger.warning(f"Usuario no encontrado: {user_id}")
                disconnect()
                return

            return f(current_user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            logger.warning("Token del WebSocket ha expirado")
            disconnect()
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token del WebSocket es inválido: {e}")
            disconnect()
        except KeyError:
            logger.warning("Header 'Authorization' no encontrado para la conexión WebSocket.")
            disconnect()
        except Exception as e:
            logger.warning(f"Error inesperado durante validación de WebSocket: {str(e)}")
            disconnect()
    return decorated_function
