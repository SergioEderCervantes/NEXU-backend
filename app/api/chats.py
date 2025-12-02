from flask import Blueprint, jsonify, g
import logging
from app.middleware.auth import token_required
from app.application.ChatService import chat_service

logger = logging.getLogger("app")

# Create the Blueprint
chats_bp = Blueprint("chats", __name__, url_prefix="/chats")


@chats_bp.route("/", methods=["GET"])
@token_required
def get_user_chats():
    """
    Get all chats for the currently authenticated user.
    For each chat, details of the other participant and a count of unread
    messages are included.
    """
    try:
        current_user_id = g.current_user.id
        chats_data = chat_service.get_chats_for_user(current_user_id)
        return jsonify({"data": chats_data}), 200
    except Exception as e:
        logger.error(f"Error retrieving chats for user {g.current_user.id}: {e}", exc_info=True)
        return jsonify(
            {"error": "Ocurrió un error inesperado al obtener los chats."}
        ), 500
