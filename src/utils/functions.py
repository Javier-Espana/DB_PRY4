from sqlalchemy import text
from database import SessionLocal

def ejecutar_funcion_sql(nombre_funcion: str, *args):
    db = SessionLocal()
    try:
        # Construir la llamada a la función SQL
        params = ", ".join(["?"] * len(args))
        query = text(f"SELECT {nombre_funcion}({params})")
        
        # Ejecutar la consulta
        result = db.execute(query, args).fetchone()
        return result[0] if result else None
    finally:
        db.close()

def calcular_total_venta_db(venta_id: int):
    return ejecutar_funcion_sql("calcular_total_venta", venta_id)

def obtener_cartas_favoritas(cliente_id: int):
    return ejecutar_funcion_sql("cartas_favoritas_cliente", cliente_id)