import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- Fernet Encryption Settings ---
    FERNET_KEY = os.getenv("FERNET_KEY", None)
    
    # --- File Storage Path ---
    BASE_PATH = os.getenv("NFS_PATH", "db")

    # --- JWT Settings ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    
    ACCESS_TOKEN_EXPIRE_MINUTES = 525600 # 1 year for development convenience

# Validación fatal: detener la aplicación si no existe JWT_SECRET_KEY
if Config.JWT_SECRET_KEY is None:
    raise RuntimeError("JWT_SECRET_KEY no está definida en el entorno. Defina JWT_SECRET_KEY y reinicie la aplicación.")
