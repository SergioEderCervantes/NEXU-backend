# --- Etapa base ---
FROM python:3.12-slim AS base

WORKDIR /app

# Evitar buffering de logs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Dependencias básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Etapa dependencias ---
FROM base AS deps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa final (runtime) ---
FROM base AS runtime

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin

# Copiar el código
COPY app/ /app/

# Comando de inicio
CMD ["python", "-m", "app.main"]
