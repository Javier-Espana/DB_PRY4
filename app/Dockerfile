# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y archivos de la app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Puerto expuesto para Streamlit
EXPOSE 8501

# Comando por defecto para ejecutar la app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]