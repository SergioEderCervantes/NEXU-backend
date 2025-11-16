from app.infraestructure.encription_service import EncryptionManager



def test_encryption():
    message = "Hola Mundo"
    manager = EncryptionManager()
    encripted = manager.encrypt_data(message)
    assert encripted != ""
    assert encripted != "Hola Mundo"
    
def test_encryption_full():
    message = "Hola Elias"
    manager = EncryptionManager()
    token = manager.encrypt_data(message)
    decrypted = manager.decrypt_data(token)
    assert decrypted == message