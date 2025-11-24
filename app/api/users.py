from flask import Blueprint, jsonify, request
import logging
from app.application.login import retrieve_users, create_user
logger = logging.getLogger("app")

# Create the Blueprint
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
def get_all_users():
    """
    Get all users from the database.
    """
    try:
       users = retrieve_users()
       return jsonify(users), 200 
    except Exception as e:
        # Log the exception e
        logger.error(e)
        return jsonify({"error": "Ocurrio un error inesperado"}), 500


@users_bp.route("/signin", methods=["POST"])
def signin():
    try:
        data = request.get_json()
        logger.debug(f"Tipo del get_json: {type(data)}")
        logger.debug(f"get_json: {data}")
        success = create_user(data)
        if success:
            return jsonify({"result": "Usuario creado correctamente"}), 201
        else:
            return jsonify({"result": "Error inesperado"}), 500
    except Exception as e:
        logger.error(e)
        return jsonify({"error": "Ocurrio un error inesperado"}), 500
