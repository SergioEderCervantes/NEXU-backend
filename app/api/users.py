from flask import Blueprint, jsonify, request, g
import logging
from pydantic import ValidationError
from app.application.LoginService import login_service
from app.application.UserService import user_service
from app.domain.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)
from app.middleware.auth import token_required

logger = logging.getLogger("app")

# Create the Blueprint
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
@token_required
def get_all_users():
    """
    Get all users from the database. Requires a valid token.
    """
    try:
        # The `current_user` is attached to `g` by the `@token_required` decorator.
        # We can add logic here, e.g., to check if g.current_user is an admin.
        # For now, we just proceed.
        users = user_service.get_all_users()
        users_dict = [user.model_dump(exclude={'password'}) for user in users]
        return jsonify({"data": users_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving all users: {e}")
        return jsonify(
            {"error": "Ocurrió un error inesperado al obtener usuarios."}
        ), 500


@users_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    """
    Get the profile of the currently logged-in user. Requires a valid token.
    """
    # The user object is attached to Flask's global `g` object by the decorator.
    current_user = g.current_user
    return jsonify({"data": current_user.model_dump(exclude={'password'})}), 200


@users_bp.route("/signup", methods=["POST"])
def signup():
    """
    Registers a new user and returns a JWT on success.
    """
    try:
        data = request.get_json()
        if not data:
            logger.warning("Signup attempt with no JSON data.")
            return jsonify({"error": "Se requiere un cuerpo de solicitud JSON."}), 400

        access_token = login_service.signup(data)
        response_data = {"access_token": access_token, "token_type": "bearer"}
        return jsonify({"data": response_data}), 201
    except ValidationError as e:
        error_details = [
            f"El campo '{err['loc'][0]}' {err['msg'].lower()}" for err in e.errors()
        ]
        logger.warning(f"Signup failed due to validation error: {error_details}")
        return jsonify({"error": "Datos de entrada inválidos.", "detalles": error_details}), 422
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
    Authenticates a user and returns a JWT on success.
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

        access_token = login_service.login(email, password)
        response_data = {"access_token": access_token, "token_type": "bearer"}
        return jsonify({"data": response_data}), 200
    except InvalidCredentialsException as e:
        logger.warning(f"Login failed: {e.message}")
        return jsonify({"error": e.message}), 401
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al iniciar sesión."}), 500


@users_bp.route("/<user_id>", methods=["GET"])
@token_required
def user_details(user_id):
    """
    Get details of a specific user by their ID. Requires a valid token.
    """
    try:
        user = user_service.get_user_by_id(user_id)
        if user:
            return jsonify({"data": user.model_dump(exclude={'password'})}), 200
        else:
            logger.warning(f"User with ID {user_id} not found.")
            return jsonify({"error": "Usuario no encontrado."}), 404
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al obtener el usuario."}), 500
