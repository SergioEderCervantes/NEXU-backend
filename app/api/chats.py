from flask import Blueprint, jsonify, g
import logging
from app.middleware.auth import token_required
from app.application.ChatService import chat_service
from app.domain.entities import Message
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
    logger.info("Iniciando conteo de chats")
    try:
        current_user_id = g.current_user.id
        chats_data = chat_service.get_chats_for_user(current_user_id)
        return jsonify({"data": chats_data}), 200
    except Exception as e:
        logger.error(f"Error retrieving chats for user {g.current_user.id}: {e}", exc_info=True)
        return jsonify(
            {"error": "Ocurrió un error inesperado al obtener los chats."}
        ), 500

@chats_bp.route("/user/<target_user_id>", methods=["GET"])
@token_required
def get_chat_by_user_id(target_user_id: str):
    """
    Get all messages for a specific chat, sorted by timestamp.
    The user must be a participant in the chat to access its messages.
    """
    try:
        current_user_id = g.current_user.id
        messages = chat_service.find_chat_by_user_ids(current_user_id, target_user_id)
        if messages is None:
            return jsonify({"data": []}), 200
        
        messages_dict = [message.model_dump() for message in messages]
        return jsonify({"data": messages_dict}), 200
        
    except Exception as e:
        logger.error(f"server error: {e}")
        return jsonify({"error": "Ha ocurrido un error inesperado"}), 500


@chats_bp.route("/<chat_id>", methods=["GET"])
@token_required
def get_chat_messages(chat_id):
    """
    Get all messages for a specific chat, sorted by timestamp.
    The user must be a participant in the chat to access its messages.
    """
    try:
        current_user_id = g.current_user.id
        
        # Verify the user is part of this chat
        chat = chat_service.chat_repository.find_by_id(chat_id)
        if not chat:
            logger.warning(f"Chat {chat_id} not found.")
            return jsonify({"data": []}), 200
        
        # Check if current user is a participant
        if current_user_id not in [chat.user_a, chat.user_b]:
            logger.warning(f"User {current_user_id} attempted to access chat {chat_id} without permission.")
            return jsonify({"error": "No tienes permiso para acceder a este chat."}), 403
        
        messages: list[Message] = chat_service.load_chat_msgs(chat, current_user_id)
        messages_dict = [message.model_dump() for message in messages]
        return jsonify({"data": messages_dict }), 200
        
    except Exception as e:
        logger.error(f"server error: {e}")
        return jsonify({"error": "Ha ocurrido un error inesperado"})
    
@chats_bp.route("/all", methods=["GET"])
def get_all():
    chats = chat_service.get_all()
    chats_dict = [chat.model_dump() for chat in chats]
    return jsonify({"data": chats_dict}), 200