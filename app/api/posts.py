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
    Optionally filters posts by tag_id if a 'filter=tag_id' query parameter is provided.
    Requires a valid token.
    """
    try:
        tag_id_filter = request.args.get('filter')
        feed = post_service.get_all_posts_for_feed(tag_id=tag_id_filter)
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

@posts_bp.route("/<post_id>", methods=["DELETE"])
@token_required
def delete_post(post_id):
    """
    Deletes a post by its ID.
    Requires a valid token and the user must be the owner of the post.
    """
    try:
        current_user_id = g.current_user.id
        if post_service.delete_post(post_id, current_user_id):
            return jsonify({"message": "Publicación eliminada exitosamente."}), 200
        else:
            return jsonify({"error": "Publicación no encontrada."}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 403 # Forbidden
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al eliminar la publicación."}), 500
