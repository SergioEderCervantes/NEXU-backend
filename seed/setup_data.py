import os
import json
from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
from app.domain.entities import DbFile

def load_users():
    # TODO: esto no deberia de estar aqui, pero por ahora funciona
    with open(os.path.join(os.path.dirname(__file__), 'usersSeed.json'), 'r') as f:
        data = json.load(f)
    
    json_data = json.dumps(data)
    
    enc_manager = EncryptionManager()
    file_manager = FileManager()
    
    encrypted_data = enc_manager.encrypt_data(json_data)
    
    file_manager.write_file(DbFile.USERS, encrypted_data)
    
def load_chats():
    with open(os.path.join(os.path.dirname(__file__), 'chatsSeed.json'), 'r') as f:
        data = json.load(f)
    
    json_data = json.dumps(data)
    
    enc_manager = EncryptionManager()
    file_manager = FileManager()
    
    encrypted_data = enc_manager.encrypt_data(json_data)
    
    file_manager.write_file(DbFile.CHATS, encrypted_data)

def load_messages():
    with open(os.path.join(os.path.dirname(__file__), 'messagesSeed.json'), 'r') as f:
        data = json.load(f)
    
    json_data = json.dumps(data)
    
    enc_manager = EncryptionManager()
    file_manager = FileManager()
    
    encrypted_data = enc_manager.encrypt_data(json_data)
    
    file_manager.write_file(DbFile.MESSAGES, encrypted_data)

def load_tags():
    with open(os.path.join(os.path.dirname(__file__), 'tagsSeed.json'), 'r') as f:
        data = json.load(f)
    
    json_data = json.dumps(data)
    
    enc_manager = EncryptionManager()
    file_manager = FileManager()
    
    encrypted_data = enc_manager.encrypt_data(json_data)
    
    file_manager.write_file(DbFile.TAGS, encrypted_data)

if __name__ == '__main__':
    load_users()
    load_chats()
    load_messages()
    load_tags()