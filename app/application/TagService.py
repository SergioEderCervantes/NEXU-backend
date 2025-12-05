import logging
from typing import List
from app.domain.entities import Tag
from app.repository.tag_repository import TagRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

logger = logging.getLogger(__name__)

class TagService:
    def __init__(self, tag_repository: TagRepository):
        self.tag_repository = tag_repository

    def get_all_tags(self) -> List[Tag]:
        """
        Retrieves all tags from the repository.
        """
        logger.info("Retrieving all tags.")
        tags = self.tag_repository.find_all()
        return tags

# Initialize dependencies for the TagService
file_manager = FileManager()
encryption_manager = EncryptionManager()
tag_repository = TagRepository(file_manager, encryption_manager)
tag_service = TagService(tag_repository)