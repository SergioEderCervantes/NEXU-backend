from typing import List, Optional
from app.domain.entities import Tag, DbFile
from app.repository.base_repository import BaseRepository
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

class TagRepository(BaseRepository[Tag]):
    """
    Repository for Tag entities. Inherits from BaseRepository but is modified
    to be read-only and to work with the 'tags' key in the JSON data file.
    """
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager):
        super().__init__(file_manager, encryption_manager, DbFile.TAGS, 'tags')

    def find_all(self) -> List[Tag]:
        """
        Retrieves all tags from the database file.
        """
        data = self._get_data()
        # The seed file uses a "tags" key.
        tags_data = data.get("tags", [])
        # The Tag entity expects aliases, but model_validate handles it automatically
        # when converting dicts to model instances.
        return [Tag.model_validate(tag) for tag in tags_data]

    def find_by_id(self, entity_id: str) -> Optional[Tag]:
        """
        Finds a tag by its ID.
        """
        data = self._get_data()
        item = next((item for item in data.get("tags", []) if item['id'] == entity_id), None)
        if item:
            return Tag.model_validate(item)
        return None

    def _to_entity(self, item: dict) -> Tag:
        return Tag(**item)

    # --- Read-only implementation: Override write methods ---

    def _save_data(self, data: dict) -> None:
        """
        Overrides base method to prevent saving data.
        """
        raise NotImplementedError("TagRepository is a read-only repository.")

    def add(self, entity: Tag) -> None:
        """
        Overrides base method to prevent adding new tags.
        """
        raise NotImplementedError("TagRepository is a read-only repository.")

    def update(self, entity: Tag) -> None:
        """
        Overrides base method to prevent updating tags.
        """
        raise NotImplementedError("TagRepository is a read-only repository.")

    def delete(self, entity_id: str) -> None:
        """
        Overrides base method to prevent deleting tags.
        """
        raise NotImplementedError("TagRepository is a read-only repository.")