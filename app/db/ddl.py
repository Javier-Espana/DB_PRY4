from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, Date, Time, Numeric, TIMESTAMP, Enum, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import text

# Configuración inicial
def generate_ddl():
    # Crear motor (no necesitamos una conexión real, solo para generar SQL)
    engine = create_engine('postgresql://user:password@localhost/dbname')
    metadata = MetaData()

    # Definir tipos ENUM personalizados
    estado_campana = PG_ENUM('planificada', 'activa', 'pausada', 'finalizada', name='estado_campana')
    tipo_donante = PG_ENUM('individual', 'empresa', name='tipo_donante')
    tipo_donacion = PG_ENUM('monetaria', 'especie', name='tipo_donacion')
    nivel_habilidad = PG_ENUM('básico', 'intermedio', 'avanzado', name='nivel_habilidad')
    tipo_contacto = PG_ENUM('email', 'teléfono', 'correo', 'sms', 'whatsapp', name='tipo_contacto')
    dia_semana = PG_ENUM('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo', name='dia_semana')

    # Definir tablas
    organizacion = Table('organizacion', metadata,
        Column('organizacion_id', Integer, primary_key=True, autoincrement=True),
        Column('nombre', String(100), nullable=False),
        Column('descripcion', Text),
        Column('email', String(100), nullable=False, unique=True),
        Column('telefono', String(20)),
        Column('direccion', Text),
        Column('sitio_web', String(100)),
        Column('fecha_registro', Date, nullable=False, server_default=text('CURRENT_DATE')),
        Column('activa', Boolean, server_default=text('TRUE')),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_email_org')
    )

    categoria = Table('categoria', metadata,
        Column('categoria_id', Integer, primary_key=True, autoincrement=True),
        Column('nombre', String(50), nullable=False, unique=True),
        Column('descripcion', Text)
    )

    sede = Table('sede', metadata,
        Column('sede_id', Integer, primary_key=True, autoincrement=True),
        Column('nombre', String(100), nullable=False),
        Column('direccion', Text, nullable=False),
        Column('ciudad', String(50), nullable=False),
        Column('region', String(50)),
        Column('codigo_postal', String(10)),
        Column('telefono', String(20)),
        Column('email', String(100)),
        Column('horario_apertura', Time),
        Column('horario_cierre', Time),
        CheckConstraint('horario_cierre > horario_apertura', name='chk_horario')
    )

    campana = Table('campana', metadata,
        Column('campana_id', Integer, primary_key=True, autoincrement=True),
        Column('organizacion_id', Integer, ForeignKey('organizacion.organizacion_id'), nullable=False),
        Column('categoria_id', Integer, ForeignKey('categoria.categoria_id')),
        Column('sede_principal_id', Integer, ForeignKey('sede.sede_id')),
        Column('nombre', String(100), nullable=False),
        Column('descripcion', Text),
        Column('fecha_inicio', Date, nullable=False),
        Column('fecha_fin', Date),
        Column('meta_monetaria', Numeric(12, 2), CheckConstraint('meta_monetaria > 0')),
        Column('estado', estado_campana, nullable=False, server_default=text("'planificada'")),
        CheckConstraint('fecha_fin IS NULL OR fecha_fin >= fecha_inicio', name='chk_fechas')
    )

    actividad = Table('actividad', metadata,
        Column('actividad_id', Integer, primary_key=True, autoincrement=True),
        Column('campana_id', Integer, ForeignKey('campana.campana_id'), nullable=False),
        Column('sede_id', Integer, ForeignKey('sede.sede_id')),
        Column('nombre', String(100), nullable=False),
        Column('descripcion', Text),
        Column('fecha_inicio', TIMESTAMP, nullable=False),
        Column('fecha_fin', TIMESTAMP, nullable=False),
        Column('capacidad_max', Integer, CheckConstraint('capacidad_max > 0')),
        CheckConstraint('fecha_fin > fecha_inicio', name='chk_fechas_actividad')
    )

    donante = Table('donante', metadata,
        Column('donante_id', Integer, primary_key=True, autoincrement=True),
        Column('tipo', tipo_donante, nullable=False),
        Column('nombre', String(50)),
        Column('apellido', String(50)),
        Column('empresa', String(100)),
        Column('email', String(100), unique=True),
        Column('telefono', String(20)),
        Column('direccion', Text),
        Column('fecha_registro', Date, nullable=False, server_default=text('CURRENT_DATE')),
        CheckConstraint(
            "(tipo = 'individual' AND apellido IS NOT NULL AND nombre IS NOT NULL AND empresa IS NULL) OR "
            "(tipo = 'empresa' AND empresa IS NOT NULL AND nombre IS NULL AND apellido IS NULL)",
            name='chk_tipo_donante'
        )
    )

    preferencia_contacto = Table('preferencia_contacto', metadata,
        Column('preferencia_id', Integer, primary_key=True, autoincrement=True),
        Column('donante_id', Integer, ForeignKey('donante.donante_id')),
        Column('tipo', tipo_contacto, nullable=False),
        Column('permitido', Boolean, server_default=text('TRUE')),
        UniqueConstraint('donante_id', 'tipo', name='uq_preferencia_contacto')
    )

    donacion = Table('donacion', metadata,
        Column('donacion_id', Integer, primary_key=True, autoincrement=True),
        Column('donante_id', Integer, ForeignKey('donante.donante_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
        Column('campana_id', Integer, ForeignKey('campana.campana_id'), nullable=False),
        Column('tipo', tipo_donacion, nullable=False),
        Column('monto', Numeric(12, 2), CheckConstraint('monto > 0')),
        Column('descripcion_especie', Text),
        Column('fecha', TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        Column('anonima', Boolean, server_default=text('FALSE')),
        Column('mensaje', Text),
        CheckConstraint(
            "(tipo = 'monetaria' AND monto IS NOT NULL AND descripcion_especie IS NULL) OR "
            "(tipo = 'especie' AND descripcion_especie IS NOT NULL)",
            name='chk_tipo_donacion'
        )
    )

    voluntario = Table('voluntario', metadata,
        Column('voluntario_id', Integer, primary_key=True, autoincrement=True),
        Column('nombre', String(50), nullable=False),
        Column('apellido', String(50), nullable=False),
        Column('email', String(100), nullable=False, unique=True),
        Column('telefono', String(20)),
        Column('direccion', Text),
        Column('fecha_nacimiento', Date, nullable=False),
        Column('fecha_registro', Date, nullable=False, server_default=text('CURRENT_DATE')),
        Column('activo', Boolean, server_default=text('TRUE')),
        CheckConstraint("fecha_nacimiento <= CURRENT_DATE - INTERVAL '16 years'", name='chk_edad'),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_email_voluntario')
    )

    disponibilidad_voluntario = Table('disponibilidad_voluntario', metadata,
        Column('disponibilidad_id', Integer, primary_key=True, autoincrement=True),
        Column('voluntario_id', Integer, ForeignKey('voluntario.voluntario_id')),
        Column('dia', dia_semana, nullable=False),
        Column('hora_inicio', Time, nullable=False),
        Column('hora_fin', Time, nullable=False),
        CheckConstraint('hora_fin > hora_inicio', name='chk_horas'),
        UniqueConstraint('voluntario_id', 'dia', 'hora_inicio', 'hora_fin', name='uq_disponibilidad')
    )

    habilidad = Table('habilidad', metadata,
        Column('habilidad_id', Integer, primary_key=True, autoincrement=True),
        Column('nombre', String(50), nullable=False, unique=True),
        Column('descripcion', Text),
        Column('categoria', String(50))
    )

    recurso = Table('recurso', metadata,
        Column('recurso_id', Integer, primary_key=True, autoincrement=True),
        Column('campana_id', Integer, ForeignKey('campana.campana_id'), nullable=False),
        Column('nombre', String(100), nullable=False),
        Column('descripcion', Text),
        Column('cantidad_requerida', Integer, CheckConstraint('cantidad_requerida > 0'), nullable=False),
        Column('cantidad_actual', Integer, CheckConstraint('cantidad_actual >= 0'), nullable=False, server_default=text('0')),
        Column('unidad_medida', String(20))
    )

    voluntario_actividad = Table('voluntario_actividad', metadata,
        Column('voluntario_id', Integer, ForeignKey('voluntario.voluntario_id'), primary_key=True),
        Column('actividad_id', Integer, ForeignKey('actividad.actividad_id'), primary_key=True),
        Column('fecha_registro', TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        Column('horas_dedicadas', Numeric(5, 2), server_default=text('0')),
        Column('comentarios', Text),
        Column('estado', String(20), server_default=text("'pendiente'"))
    )

    voluntario_habilidad = Table('voluntario_habilidad', metadata,
        Column('voluntario_id', Integer, ForeignKey('voluntario.voluntario_id'), primary_key=True),
        Column('habilidad_id', Integer, ForeignKey('habilidad.habilidad_id'), primary_key=True),
        Column('nivel', nivel_habilidad, nullable=False, server_default=text("'básico'")),
        Column('anios_experiencia', Integer, CheckConstraint('anios_experiencia >= 0')),
        Column('certificado', Boolean, server_default=text('FALSE'))
    )

    estadisticas_campana = Table('estadisticas_campana', metadata,
        Column('campana_id', Integer, ForeignKey('campana.campana_id'), primary_key=True),
        Column('monto_recaudado', Numeric(12, 2), server_default=text('0')),
        Column('porcentaje_meta', Numeric(5, 2), server_default=text('0')),
        Column('num_donaciones', Integer, server_default=text('0')),
        Column('num_voluntarios', Integer, server_default=text('0')),
        Column('ultima_actualizacion', TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    )

    # Generar el DDL
    ddl = []
    
    # Agregar tipos ENUM primero
    for enum in [estado_campana, tipo_donante, tipo_donacion, nivel_habilidad, tipo_contacto, dia_semana]:
        ddl.append(str(CreateType(enum).compile(engine)))
    
    # Agregar tablas
    for table in metadata.sorted_tables:
        ddl.append(str(CreateTable(table).compile(engine)))
    
    # Agregar triggers (como texto directamente ya que SQLAlchemy no los soporta directamente)
    triggers = [
        """
        CREATE OR REPLACE FUNCTION actualizar_estadisticas_donacion()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.tipo = 'monetaria' THEN
                UPDATE estadisticas_campana
                SET monto_recaudado = monto_recaudado + NEW.monto,
                    num_donaciones = num_donaciones + 1,
                    porcentaje_meta = (
                        SELECT CASE WHEN meta_monetaria > 0 
                               THEN ((monto_recaudado + NEW.monto) / meta_monetaria) * 100
                               ELSE 0 
                               END
                        FROM campana WHERE campana_id = NEW.campana_id
                    ),
                    ultima_actualizacion = CURRENT_TIMESTAMP
                WHERE campana_id = NEW.campana_id;
            ELSE
                UPDATE estadisticas_campana
                SET num_donaciones = num_donaciones + 1,
                    ultima_actualizacion = CURRENT_TIMESTAMP
                WHERE campana_id = NEW.campana_id;
            END IF;
            
            IF NOT FOUND THEN
                INSERT INTO estadisticas_campana (
                    campana_id, 
                    monto_recaudado, 
                    porcentaje_meta,
                    num_donaciones
                ) VALUES (
                    NEW.campana_id, 
                    CASE WHEN NEW.tipo = 'monetaria' THEN NEW.monto ELSE 0 END,
                    (
                        SELECT CASE WHEN meta_monetaria > 0 
                               THEN (CASE WHEN NEW.tipo = 'monetaria' THEN NEW.monto ELSE 0 END / meta_monetaria) * 100
                               ELSE 0 
                               END
                        FROM campana WHERE campana_id = NEW.campana_id
                    ),
                    1
                );
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER after_donacion_insert
        AFTER INSERT ON donacion
        FOR EACH ROW
        EXECUTE FUNCTION actualizar_estadisticas_donacion();
        """,
        """
        CREATE OR REPLACE FUNCTION actualizar_estadisticas_voluntario()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE estadisticas_campana
            SET num_voluntarios = (
                    SELECT COUNT(DISTINCT va.voluntario_id) 
                    FROM voluntario_actividad va
                    JOIN actividad a ON va.actividad_id = a.actividad_id
                    WHERE a.campana_id = (
                        SELECT campana_id FROM actividad WHERE actividad_id = NEW.actividad_id
                    )
                ),
                ultima_actualizacion = CURRENT_TIMESTAMP
            WHERE campana_id = (
                SELECT campana_id FROM actividad WHERE actividad_id = NEW.actividad_id
            );
            
            IF NOT FOUND THEN
                INSERT INTO estadisticas_campana (
                    campana_id,
                    num_voluntarios
                ) VALUES (
                    (SELECT campana_id FROM actividad WHERE actividad_id = NEW.actividad_id),
                    1
                );
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER after_voluntario_actividad_insert
        AFTER INSERT ON voluntario_actividad
        FOR EACH ROW
        EXECUTE FUNCTION actualizar_estadisticas_voluntario();
        """,
        """
        CREATE OR REPLACE FUNCTION actualizar_estado_campana()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE campana
            SET estado = 
                CASE
                    WHEN fecha_inicio > CURRENT_DATE THEN 'planificada'
                    WHEN fecha_fin IS NULL AND fecha_inicio <= CURRENT_DATE THEN 'activa'
                    WHEN fecha_fin <= CURRENT_DATE THEN 'finalizada'
                    WHEN fecha_inicio <= CURRENT_DATE AND fecha_fin > CURRENT_DATE THEN 'activa'
                    ELSE estado
                END
            WHERE campana_id = NEW.campana_id;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER after_campana_date_update
        BEFORE INSERT OR UPDATE OF fecha_inicio, fecha_fin ON campana
        FOR EACH ROW
        EXECUTE FUNCTION actualizar_estado_campana();
        """
    ]
    
    ddl.extend(triggers)
    
    # Escribir a archivo
    with open('DDL.sql', 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(ddl))
    
    print("Archivo DDL.sql generado exitosamente!")

# Clase auxiliar para crear tipos ENUM
class CreateType:
    def __init__(self, enum_type):
        self.enum_type = enum_type
    
    def compile(self, engine):
        return f"CREATE TYPE {self.enum_type.name} AS ENUM ({', '.join(['\'{}\''.format(v) for v in self.enum_type.enums])});"

if __name__ == '__main__':
    generate_ddl()
    