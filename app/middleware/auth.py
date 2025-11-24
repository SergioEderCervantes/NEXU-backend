import functools
import jwt
from flask import request, jsonify, g
from app.config.settings import Config
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            user_id = payload['sub']

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
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

        return f(*args, **kwargs)
    return decorated_function
