# migrations/triggers.py
from sqlalchemy import text
from db.connection import get_engine

def create_triggers():
    engine = get_engine()
    with engine.connect() as conn:
        # Función para actualizar estadísticas
        conn.execute(text("""
        CREATE OR REPLACE FUNCTION actualizar_estadisticas_campana()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Lógica del trigger
        END;
        $$ LANGUAGE plpgsql;
        """))
        
        # Trigger para donaciones
        conn.execute(text("""
        CREATE TRIGGER tr_actualizar_estadisticas
        AFTER INSERT OR UPDATE OR DELETE ON donacion
        FOR EACH ROW EXECUTE FUNCTION actualizar_estadisticas_campana();
        """))
        
        conn.commit()