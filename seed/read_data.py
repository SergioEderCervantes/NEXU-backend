from app.infraestructure.encription_service import EncryptionManager
from app.infraestructure.file_service import FileManager
from app.domain.entities import DbFile

def print_users():
    # TODO: esto no deberia de estar aqui, pero por ahora funciona
    enc_manager = EncryptionManager()
    file_manager = FileManager()
    
    token = file_manager.read_file(DbFile.USERS)
    msg = enc_manager.decrypt_data(token)
    print(msg)


if __name__ == '__main__':
    print_users()