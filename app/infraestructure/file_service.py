from app.domain.entities import DbFile
# Servicio responsable solo de leer y escribir datos en archivos
class FileManager:
    def read_file(self, file: DbFile) -> bytes:
        """
        Lee un archivo binario desde la ruta especificada en el enum.
        """
        try:
            with open(file.value, "rb") as f:
                return f.read()
        except FileNotFoundError:
            # Si el archivo no existe, devuelve bytes vacíos.
            return b''

    def write_file(self, file: DbFile, data: bytes) -> bool:
        """
        Escribe datos binarios en la ruta especificada en el enum.
        Devuelve True si la escritura fue exitosa, False si ocurrió algún error.
        """
        try:
            with open(file.value, "wb") as f:
                f.write(data)
            return True
        except Exception:
            return False