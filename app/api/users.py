from flask import Blueprint, jsonify, request
import logging
from pydantic import ValidationError
from app.application.LoginService import login_service
from app.domain.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)

logger = logging.getLogger("app")

# Create the Blueprint
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
def get_all_users():
    """
    Get all users from the database.
    """
    try:
        users = login_service.get_all_users()
        # Pydantic models must be converted to dicts for JSON serialization
        users_dict = [user.model_dump() for user in users]
        return jsonify(users_dict), 200
    except Exception as e:
        logger.error(f"Error retrieving all users: {e}")
        return jsonify(
            {"error": "Ocurrió un error inesperado al obtener usuarios."}
        ), 500


@users_bp.route("/signup", methods=["POST"])
def signup():
    """
    Registers a new user.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Signup attempt with no JSON data.")
            return jsonify({"error": "Se requiere un cuerpo de solicitud JSON."}), 400

        new_user = login_service.signup(data)
        return jsonify(new_user.model_dump()), 201
    except ValidationError as e:
        # Pydantic's validation errors are parsed into a more user-friendly format.
        error_details = [
            f"El campo '{err['loc'][0]}' {err['msg'].lower()}" for err in e.errors()
        ]
        logger.warning(f"Signup failed due to validation error: {error_details}")
        return jsonify({"error": "Datos de entrada inválidos.", "detalles": error_details}), 400
    except UserAlreadyExistsException as e:
        logger.warning(f"Signup failed: {e.message}")
        return jsonify({"error": e.message}), 409
    except ValueError as e:
        logger.warning(f"Signup failed due to bad request: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}", exc_info=True)
        return jsonify(
            {"error": "Ocurrió un error inesperado al registrar el usuario."}
        ), 500


@users_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user and returns user data if successful.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Login attempt with no JSON data.")
            return jsonify({"error": "Se requiere un cuerpo de solicitud JSON."}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            logger.warning("Login attempt with missing email or password.")
            return jsonify({"error": "Email y contraseña son requeridos."}), 400

        user = login_service.login(email, password)
        # For security, you might want to return a subset of user data or a token
        return jsonify(user.model_dump()), 200
    except InvalidCredentialsException as e:
        logger.warning(f"Login failed: {e.message}")
        return jsonify({"error": e.message}), 401
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al iniciar sesión."}), 500
