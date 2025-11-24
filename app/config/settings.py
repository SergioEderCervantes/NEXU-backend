import os
import binascii
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- Fernet Encryption Settings ---
    FERNET_KEY = os.getenv("FERNET_KEY", None)
    
    # --- File Storage Path ---
    BASE_PATH = os.getenv("NFS_PATH", "db")

    # --- JWT Settings ---
    # In production, this MUST be a persistent, securely stored key loaded from the environment.
    # For development, we generate one, but it will change on each server restart.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", binascii.hexlify(os.urandom(32)).decode())
    JWT_ALGORITHM = "HS256"
    
    # WARNING: Long-lived tokens are for development ONLY. Use short-lived tokens (e.g., 15-60 mins) in production.
    ACCESS_TOKEN_EXPIRE_MINUTES = 525600 # 1 year for development convenience
