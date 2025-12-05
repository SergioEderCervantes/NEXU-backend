import logging
from flask import Blueprint, jsonify
from app.application.TagService import tag_service
from app.middleware.auth import token_required

logger = logging.getLogger("app")

# Create the Blueprint for tags
tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

@tags_bp.route("/", methods=["GET"])
@token_required
def get_all_tags():
    """
    Get all available tags from the database.
    Requires a valid token.
    """
    try:
        tags = tag_service.get_all_tags()
        # Use model_dump to convert the Pydantic models to dictionaries
        tags_dict = [tag.model_dump(by_alias=True) for tag in tags]
        return jsonify({"data": tags_dict}), 200
    except Exception as e:
        logger.error(f"Error retrieving all tags: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al obtener los tags."}), 500