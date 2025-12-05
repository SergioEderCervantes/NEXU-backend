import logging
from typing import List, Dict, Any
from app.repository.post_repository import PostRepository
from app.repository.user_repository import UserRepository
from app.repository.tag_repository import TagRepository
from app.domain.entities import Post
from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
logger = logging.getLogger(__name__)


class PostService:
    def __init__(
        self,
        post_repository: PostRepository,
        user_repository: UserRepository,
        tag_repository: TagRepository,
    ):
        self.post_repository = post_repository
        self.user_repository = user_repository
        self.tag_repository = tag_repository

    def get_all_posts_for_feed(self) -> List[Dict[str, Any]]:
        """
        Retrieves all posts and enriches them with user and tag information for the feed.
        """
        logger.info("Retrieving all posts for the feed.")
        posts = self.post_repository.find_all()
        users = self.user_repository.find_all()
        tags = self.tag_repository.find_all()

        user_map = {user.id: user for user in users}
        tag_map = {tag.id: tag for tag in tags}

        feed = []
        for post in posts:
            user = user_map.get(post.user_id)
            tag = tag_map.get(post.tag_id)

            if user and tag:
                feed.append(
                    {
                        "id": post.id,
                        "description": post.description,
                        "timestamp": post.timestamp,
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "career": user.career,
                            "avatar_url": user.avatar_url,
                        },
                        "tag": {
                            "id": tag.id,
                            "name": tag.name,
                        },
                    }
                )

        # Sort feed by timestamp, newest first
        feed.sort(key=lambda x: x["timestamp"], reverse=True)

        return feed

    def create_post(self, user_id: str, tag_id: str, description: str) -> Post:
        """
        Creates a new post.
        """
        logger.info(f"Creating a new post for user {user_id}.")
        post = Post(user_id=user_id, tag_id=tag_id, description=description)
        self.post_repository.add(post)
        logger.info(f"Successfully created post {post.id} for user {user_id}.")
        return post


# Dependency-injected instance of the service

file_manager = FileManager()
encryption_manager = EncryptionManager()
tag_repository = TagRepository(file_manager, encryption_manager)
user_repository = UserRepository(file_manager, encryption_manager)
post_repository = PostRepository(file_manager, encryption_manager)
post_service = PostService(post_repository, user_repository, tag_repository)
