import logging
from flask import Blueprint, jsonify, request, g
from app.application.PostService import post_service
from app.middleware.auth import token_required

logger = logging.getLogger("app")

# Create the Blueprint for posts
posts_bp = Blueprint("posts", __name__, url_prefix="/posts")

@posts_bp.route("/", methods=["GET"])
@token_required
def get_posts():
    """
    Get all posts for the feed, enriched with user and tag information.
    Requires a valid token.
    """
    try:
        feed = post_service.get_all_posts_for_feed()
        return jsonify({"data": feed}), 200
    except Exception as e:
        logger.error(f"Error retrieving posts for feed: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al obtener las publicaciones."}), 500

@posts_bp.route("/", methods=["POST"])
@token_required
def create_post():
    """
    Creates a new post.
    Requires a valid token.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Se requiere un cuerpo de solicitud JSON."}), 400

        current_user_id = g.current_user.id
        tag_id = data.get("tag_id")
        description = data.get("description")

        if not tag_id or not description:
            return jsonify({"error": "tag_id y description son requeridos."}), 400

        post = post_service.create_post(current_user_id, tag_id, description)
        return jsonify({"data": post.model_dump()}), 201
    except Exception as e:
        logger.error(f"Error creating post: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al crear la publicación."}), 500
