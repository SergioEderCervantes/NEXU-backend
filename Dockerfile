FROM python:3.12-slim

WORKDIR /app

# Evitar buffering de logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY app/ /app/

# Copiar test
COPY tests/ /app/tests

# Comando de inicio
CMD ["python", "-m", "app.main"]
