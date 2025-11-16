from cryptography.fernet import Fernet, InvalidToken
from app.config.settings import Config
import logging
from app.utils.timed import timed_task
# Servicio encargado solamente de encriptar y desencriptar datos

logger = logging.getLogger('app')

class EncryptionManager:
    def __init__(self) -> None:
        if not Config.FERNET_KEY:
            raise ValueError("FERNET_KEY no está definida en las variables de entorno.")
        try:
            self.fernet = Fernet(self.load_key(Config.FERNET_KEY))
        except (InvalidToken, TypeError) as e:
            raise ValueError("Error al cargar la clave Fernet: " + str(e))
    
    @timed_task("encrypt_data")
    def encrypt_data(self, data: str) -> bytes:
        try:
            data_bytes = data.encode()
            return self.fernet.encrypt(data_bytes)
        except Exception as e:
            raise RuntimeError("Error al encriptar los datos: " + str(e))

    @timed_task("decrypt_data")
    def decrypt_data(self, token: bytes) -> str:
        try:
            data_bytes = self.fernet.decrypt(token)
            return data_bytes.decode()
        except (InvalidToken, TypeError, ValueError) as e:
            raise ValueError("Error al desencriptar el token: " + str(e))
        
        
    def load_key(self, key: str) -> bytes:
        return key.encode()