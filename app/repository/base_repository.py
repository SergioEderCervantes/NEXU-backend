from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from jsonpath_ng.ext import parse
import json
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import BaseEntity, DbFile
import logging

logger = logging.getLogger('app')

T = TypeVar('T', bound=BaseEntity)

class BaseRepository(ABC, Generic[T]):
    """
    Abstract Base Class for repositories, providing common CRUD (Create, Read, Update, Delete)
    operations for entities stored in encrypted JSON files.
    It handles reading from and writing to encrypted data files, and manages the structure
    of the data within these files.
    """
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager, db_file: DbFile, entity_name: str):
        """
        Initializes the BaseRepository with necessary dependencies for file management and encryption.

        Args:
            file_manager (FileManager): Service to handle file read/write operations.
            encryption_manager (EncryptionManager): Service to handle data encryption/decryption.
            db_file (DbFile): Enum specifying the target data file.
            entity_name (str): The key under which entities are stored in the JSON data (e.g., 'users').
        """
        self.file_manager = file_manager
        self.encryption_manager = encryption_manager
        self.db_file = db_file
        self.entity_name = entity_name

    def _get_data(self) -> dict:
        """
        Reads encrypted data from the file, decrypts it, and parses it into a dictionary.
        Returns an empty dictionary with the entity_name key if the file is empty or missing.
        """
        encrypted_data = self.file_manager.read_file(self.db_file)
        if not encrypted_data:
            return {self.entity_name: []}
        decrypted_data = self.encryption_manager.decrypt_data(encrypted_data)
        logger.debug(f"Data desencriptado: {decrypted_data}")
        return json.loads(decrypted_data)

    def _save_data(self, data: dict):
        """
        Serializes the given data dictionary to JSON, encrypts it, and writes it to the file.

        Args:
            data (dict): The dictionary containing all entities to be saved.
        """
        json_data = json.dumps(data, indent=4, default=str)
        encrypted_data = self.encryption_manager.encrypt_data(json_data)
        self.file_manager.write_file(self.db_file, encrypted_data)

    @abstractmethod
    def _to_entity(self, item: dict) -> T:
        """
        Abstract method to convert a dictionary item read from the database into a domain entity object.
        Subclasses must implement this method.

        Args:
            item (dict): The dictionary representation of an entity.

        Returns:
            T: An instance of the domain entity.
        """
        pass

    def find_all(self) -> List[T]:
        """
        Retrieves all entities of the specified type from the repository.

        Returns:
            List[T]: A list of domain entity objects.
        """
        data = self._get_data()
        jsonpath_expression = parse(f'$.{self.entity_name}[*]')
        matches = jsonpath_expression.find(data)
        return [self._to_entity(match.value) for match in matches]

    def find_by_attribute(self, attribute: str, value) -> Optional[T]:
        """
        Finds an entity by a specific attribute and its value.

        Args:
            attribute (str): The name of the attribute to search by.
            value: The value of the attribute to match.

        Returns:
            Optional[T]: The found entity, or None if no entity matches.
        """
        data = self._get_data()
        query_value = f'"{value}"' if isinstance(value, str) else value
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.{attribute} == {query_value})]')
        matches = jsonpath_expression.find(data)
        if matches:
            return self._to_entity(matches[0].value)
        return None

    def find_by_id(self, entity_id: str) -> Optional[T]:
        """
        Finds an entity by its unique ID.

        Args:
            entity_id (int): The ID of the entity to find.

        Returns:
            Optional[T]: The found entity, or None if no entity with the given ID exists.
        """
        return self.find_by_attribute('id', entity_id)

    def add(self, entity: T) -> T:
        """
        Adds a new entity to the repository.

        Args:
            entity (T): The domain entity object to add.

        Returns:
            T: The added entity object.
        """
        data = self._get_data()
        data[self.entity_name].append(entity.model_dump())
        self._save_data(data)
        return entity

    def update(self, entity: T) -> Optional[T]:
        """
        Updates an existing entity in the repository based on its ID.

        Args:
            entity (T): The domain entity object with updated data.

        Returns:
            Optional[T]: The updated entity object if found and updated, otherwise None.
        """
        data = self._get_data()
        query_id = f'"{entity.id}"' if isinstance(entity.id, str) else entity.id
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.id == {query_id})]')
        if jsonpath_expression.update(data, entity.model_dump()):
            self._save_data(data)
            return entity
        return None

    def delete(self, entity_id: str) -> bool:
        """
        Deletes an entity from the repository by its ID.

        Args:
            entity_id (int): The ID of the entity to delete.

        Returns:
            bool: True if the entity was found and deleted, False otherwise.
        """
        data = self._get_data()
        query_id = f'"{entity_id}"' if isinstance(entity_id, str) else entity_id
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.id == {query_id})]')
        if jsonpath_expression.find(data):
            updated_items = [item for item in data[self.entity_name] if item['id'] != entity_id]
            data[self.entity_name] = updated_items
            self._save_data(data)
            return True
        return False
