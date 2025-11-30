import bcrypt

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt. Genera un salt y devuelve el hash completo.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash de bcrypt.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except ValueError:
        # This can happen if the stored hash is not a valid bcrypt hash
        return False
