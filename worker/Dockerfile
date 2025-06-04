FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del worker
COPY . .

# Crear directorio para mensajes y establecer permisos
RUN mkdir -p /app/messages && chown -R 1000:1000 /app/messages
USER 1000

# Comando para iniciar el worker (¡IMPORTANTE! No usar uvicorn aquí)
CMD ["python", "worker.py"]