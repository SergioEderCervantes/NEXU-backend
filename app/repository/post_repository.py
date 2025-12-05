from app.domain.entities import Post, DbFile
from app.repository.base_repository import BaseRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

class PostRepository(BaseRepository[Post]):
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager):
        super().__init__(
            file_manager,
            encryption_manager,
            DbFile.POSTS,
            'posts'
        )

    def _to_entity(self, item: dict) -> Post:
        """
        Converts a dictionary representation of a post into a Post domain entity object.
        """
        return Post(**item)

