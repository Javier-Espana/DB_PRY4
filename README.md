# DB_PRY4
## Integrantes
#### Angel Esquit - 23221
#### Javier España - 23361

## Pasos para ejecutar
### Construir y levantar los contenedores
```bash
docker compose up --build
```
Una vez iniciada, abre tu navegador en: http://localhost:8501

## Inicialización de la base de datos (ORM)
1. Asegúrate de tener las dependencias instaladas (ver requirements.txt).
2. Ejecuta la inicialización de la base de datos usando SQLAlchemy ORM:
   - Puedes usar la función `init_db()` de `app/db/connection.py` para crear las tablas.
3. Para poblar la base de datos con datos de prueba usando el ORM, ejecuta la función `poblar_db_orm(session)` de `app/db/registros.py`.

> Los archivos `database/DDL.sql` y `database/Registros.sql` son solo de referencia para la estructura y datos iniciales.
