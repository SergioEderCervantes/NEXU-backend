import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FERNET_KEY = os.getenv("FERNET_KEY", None)
    BASE_PATH = os.getenv("NFS_PATH", "db")
