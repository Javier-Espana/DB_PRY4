#!/bin/bash
set -e

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté lista..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  sleep 2
done

echo "Base de datos lista."

# Generar archivos DDL.sql y Registros.sql si no existen
if [ ! -f /database/DDL.sql ] || [ ! -f /database/Registros.sql ]; then
  echo "Generando archivos DDL.sql y Registros.sql..."
  python3 /app/db/ddl.py
  python3 /app/db/registros.py
fi

# Inicializar la base de datos (tablas y datos)
python3 -c "from db.connection import init_db; init_db()"
python3 -c "from db.registros import poblar_db_orm; from db.connection import get_session; poblar_db_orm(get_session())"

# Ejecutar el backend (Streamlit)
streamlit run /app/main.py --server.port=8501 --server.address=0.0.0.0
