from app.domain.entities import DbFile
from app.infraestructure.file_service import FileManager
from app.infraestructure.encription_service import EncryptionManager

def test_write():
    message = b"Hola soy un texto binario"
    manager = FileManager()
    result = manager.write_file(DbFile.TEST,message)
    assert result
    
    

def test_read():
    manager = FileManager()
    message = manager.read_file(DbFile.TEST)
    assert message == b"Hola soy un texto binario"
    
# Test de integracion con el servicio de encriptacion

def test_write_with_encryption():
    assert FileManager().write_file(DbFile.TEST,EncryptionManager().encrypt_data("Hola Mundo"))

def test_read_with_decryption():
    enc_man = EncryptionManager()
    file_man = FileManager()
    encripted = file_man.read_file(DbFile.TEST)
    message = enc_man.decrypt_data(encripted)
    assert message != ""
    assert message == "Hola Mundo"