# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y gcc libpq-dev postgresql-client && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y archivos de la app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Asegurar permisos de ejecución para el entrypoint
RUN chmod +x /app/entrypoint.sh

# Puerto expuesto para Streamlit
EXPOSE 8501

# El entrypoint lo define docker-compose, pero por claridad:
ENTRYPOINT ["/app/entrypoint.sh"]