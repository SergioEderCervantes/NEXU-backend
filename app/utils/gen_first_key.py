from cryptography.fernet import Fernet

# TODO: Borrar este archivo en produccion, creo que no da riesgos de seguridad pero por si acaso

if __name__ == "__main__":
    print("Generando la llave criptografica de Fernet...")
    key = Fernet.generate_key()
    print("Llave generada, copia y pegala en tu .env para poder arrancar los servicios (con comillas sin la b inicial)")
    print(key)