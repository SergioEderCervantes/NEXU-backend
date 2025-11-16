from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from jsonpath_ng.ext import parse
import json
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager
from app.domain.entities import BaseEntity, DbFile

T = TypeVar('T', bound=BaseEntity)

class BaseRepository(ABC, Generic[T]):
    def __init__(self, file_manager: FileManager, encryption_manager: EncryptionManager, db_file: DbFile, entity_name: str):
        self.file_manager = file_manager
        self.encryption_manager = encryption_manager
        self.db_file = db_file
        self.entity_name = entity_name

    def _get_data(self) -> dict:
        encrypted_data = self.file_manager.read_file(self.db_file)
        if not encrypted_data:
            return {self.entity_name: []}
        decrypted_data = self.encryption_manager.decrypt_data(encrypted_data)
        return json.loads(decrypted_data)

    def _save_data(self, data: dict):
        json_data = json.dumps(data, indent=4)
        encrypted_data = self.encryption_manager.encrypt_data(json_data)
        self.file_manager.write_file(self.db_file, encrypted_data)

    @abstractmethod
    def _to_entity(self, item: dict) -> T:
        pass

    def find_all(self) -> List[T]:
        data = self._get_data()
        jsonpath_expression = parse(f'$.{self.entity_name}[*]')
        matches = jsonpath_expression.find(data)
        return [self._to_entity(match.value) for match in matches]

    def find_by_attribute(self, attribute: str, value) -> Optional[T]:
        data = self._get_data()
        query_value = f'"{value}"' if isinstance(value, str) else value
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.{attribute} == {query_value})]')
        matches = jsonpath_expression.find(data)
        if matches:
            return self._to_entity(matches[0].value)
        return None

    def find_by_id(self, entity_id: int) -> Optional[T]:
        return self.find_by_attribute('id', entity_id)

    def add(self, entity: T) -> T:
        data = self._get_data()
        data[self.entity_name].append(entity.model_dump())
        self._save_data(data)
        return entity

    def update(self, entity: T) -> Optional[T]:
        data = self._get_data()
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.id == {entity.id})]')
        if jsonpath_expression.update(data, entity.model_dump()):
            self._save_data(data)
            return entity
        return None

    def delete(self, entity_id: int) -> bool:
        data = self._get_data()
        jsonpath_expression = parse(f'$.{self.entity_name}[?(@.id == {entity_id})]')
        if jsonpath_expression.find(data):
            updated_items = [item for item in data[self.entity_name] if item['id'] != entity_id]
            data[self.entity_name] = updated_items
            self._save_data(data)
            return True
        return False
