from flask import Blueprint, jsonify
from app.repository.user_repository import UserRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

# Create instances of the services and repository
# In a real app, this would be handled by a dependency injection container
file_manager = FileManager()
encryption_manager = EncryptionManager()
user_repository = UserRepository(file_manager, encryption_manager)

# Create the Blueprint
users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/', methods=['GET'])
def get_all_users():
    """
    Get all users from the database.
    """
    try:
        users = user_repository.find_all()
        # Pydantic models must be converted to dicts for JSON serialization
        users_dict = [user.model_dump() for user in users]
        return jsonify(users_dict), 200
    except Exception as e:
        # Log the exception e
        return jsonify({"error": "An unexpected error occurred."}), 500
