from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Time, Numeric, ForeignKey, Enum, TIMESTAMP, CheckConstraint, UniqueConstraint, text
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

# Enums
class EstadoCampanaEnum(enum.Enum):
    planificada = 'planificada'
    activa = 'activa'
    pausada = 'pausada'
    finalizada = 'finalizada'

class TipoDonanteEnum(enum.Enum):
    individual = 'individual'
    empresa = 'empresa'

class TipoDonacionEnum(enum.Enum):
    monetaria = 'monetaria'
    especie = 'especie'

class NivelHabilidadEnum(enum.Enum):
    basico = 'básico'
    intermedio = 'intermedio'
    avanzado = 'avanzado'

class TipoContactoEnum(enum.Enum):
    email = 'email'
    telefono = 'teléfono'
    correo = 'correo'
    sms = 'sms'
    whatsapp = 'whatsapp'

class DiaSemanaEnum(enum.Enum):
    lunes = 'lunes'
    martes = 'martes'
    miercoles = 'miércoles'
    jueves = 'jueves'
    viernes = 'viernes'
    sabado = 'sábado'
    domingo = 'domingo'

# Tablas principales
class Organizacion(Base):
    __tablename__ = 'organizacion'
    organizacion_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    email = Column(String(100), nullable=False, unique=True)
    telefono = Column(String(20))
    direccion = Column(Text)
    sitio_web = Column(String(100))
    fecha_registro = Column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    activa = Column(Boolean, server_default=text('TRUE'))
    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_email_org'),
    )
    campanas = relationship('Campana', back_populates='organizacion')

class Categoria(Base):
    __tablename__ = 'categoria'
    categoria_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    campanas = relationship('Campana', back_populates='categoria')

class Sede(Base):
    __tablename__ = 'sede'
    sede_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(50), nullable=False)
    region = Column(String(50))
    codigo_postal = Column(String(10))
    telefono = Column(String(20))
    email = Column(String(100))
    horario_apertura = Column(Time)
    horario_cierre = Column(Time)
    __table_args__ = (
        CheckConstraint('horario_cierre > horario_apertura', name='chk_horario'),
    )
    campanas = relationship('Campana', back_populates='sede_principal')

class Campana(Base):
    __tablename__ = 'campana'
    campana_id = Column(Integer, primary_key=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey('organizacion.organizacion_id'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categoria.categoria_id'))
    sede_principal_id = Column(Integer, ForeignKey('sede.sede_id'))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    meta_monetaria = Column(Numeric(12, 2), CheckConstraint('meta_monetaria > 0'))
    estado = Column(Enum(EstadoCampanaEnum), nullable=False, server_default=text("'planificada'"))
    __table_args__ = (
        CheckConstraint('fecha_fin IS NULL OR fecha_fin >= fecha_inicio', name='chk_fechas'),
    )
    organizacion = relationship('Organizacion', back_populates='campanas')
    categoria = relationship('Categoria', back_populates='campanas')
    sede_principal = relationship('Sede', back_populates='campanas')
    actividades = relationship('Actividad', back_populates='campana')
    donaciones = relationship('Donacion', back_populates='campana', cascade='all, delete-orphan')
    recursos = relationship('Recurso', back_populates='campana', cascade='all, delete-orphan')
    estadisticas = relationship('EstadisticasCampana', back_populates='campana', uselist=False, cascade='all, delete-orphan')

class Actividad(Base):
    __tablename__ = 'actividad'
    actividad_id = Column(Integer, primary_key=True, autoincrement=True)
    campana_id = Column(Integer, ForeignKey('campana.campana_id'), nullable=False)
    sede_id = Column(Integer, ForeignKey('sede.sede_id'))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(TIMESTAMP, nullable=False)
    fecha_fin = Column(TIMESTAMP, nullable=False)
    capacidad_max = Column(Integer, CheckConstraint('capacidad_max > 0'))
    __table_args__ = (
        CheckConstraint('fecha_fin > fecha_inicio', name='chk_fechas_actividad'),
    )
    campana = relationship('Campana', back_populates='actividades')
    voluntarios = relationship('VoluntarioActividad', back_populates='actividad', cascade='all, delete-orphan')
    sede = relationship('Sede')

class Donante(Base):
    __tablename__ = 'donante'
    donante_id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum(TipoDonanteEnum), nullable=False)
    nombre = Column(String(50))
    apellido = Column(String(50))
    empresa = Column(String(100))
    email = Column(String(100), unique=True)
    telefono = Column(String(20))
    direccion = Column(Text)
    fecha_registro = Column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    __table_args__ = (
        CheckConstraint(
            "(tipo = 'individual' AND apellido IS NOT NULL AND nombre IS NOT NULL AND empresa IS NULL) OR "
            "(tipo = 'empresa' AND empresa IS NOT NULL AND nombre IS NULL AND apellido IS NULL)",
            name='chk_tipo_donante'
        ),
    )
    donaciones = relationship('Donacion', back_populates='donante', cascade='all, delete-orphan')
    preferencias_contacto = relationship('PreferenciaContacto', back_populates='donante', cascade='all, delete-orphan')

class PreferenciaContacto(Base):
    __tablename__ = 'preferencia_contacto'
    preferencia_id = Column(Integer, primary_key=True, autoincrement=True)
    donante_id = Column(Integer, ForeignKey('donante.donante_id'))
    tipo = Column(Enum(TipoContactoEnum), nullable=False)
    permitido = Column(Boolean, server_default=text('TRUE'))
    __table_args__ = (
        UniqueConstraint('donante_id', 'tipo', name='uq_preferencia_contacto'),
    )
    donante = relationship('Donante', back_populates='preferencias_contacto')

class Donacion(Base):
    __tablename__ = 'donacion'
    donacion_id = Column(Integer, primary_key=True, autoincrement=True)
    donante_id = Column(Integer, ForeignKey('donante.donante_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    campana_id = Column(Integer, ForeignKey('campana.campana_id'), nullable=False)
    tipo = Column(Enum(TipoDonacionEnum), nullable=False)
    monto = Column(Numeric(12, 2), CheckConstraint('monto > 0'))
    descripcion_especie = Column(Text)
    fecha = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    anonima = Column(Boolean, server_default=text('FALSE'))
    mensaje = Column(Text)
    __table_args__ = (
        CheckConstraint(
            "(tipo = 'monetaria' AND monto IS NOT NULL AND descripcion_especie IS NULL) OR "
            "(tipo = 'especie' AND descripcion_especie IS NOT NULL)",
            name='chk_tipo_donacion'
        ),
    )
    campana = relationship('Campana', back_populates='donaciones')
    donante = relationship('Donante', back_populates='donaciones')

class Voluntario(Base):
    __tablename__ = 'voluntario'
    voluntario_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    telefono = Column(String(20))
    direccion = Column(Text)
    fecha_nacimiento = Column(Date, nullable=False)
    fecha_registro = Column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    activo = Column(Boolean, server_default=text('TRUE'))
    __table_args__ = (
        CheckConstraint("fecha_nacimiento <= CURRENT_DATE - INTERVAL '16 years'", name='chk_edad'),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_email_voluntario'),
    )
    disponibilidades = relationship('DisponibilidadVoluntario', back_populates='voluntario', cascade='all, delete-orphan')
    actividades = relationship('VoluntarioActividad', back_populates='voluntario', cascade='all, delete-orphan')
    habilidades = relationship('VoluntarioHabilidad', back_populates='voluntario', cascade='all, delete-orphan')

class DisponibilidadVoluntario(Base):
    __tablename__ = 'disponibilidad_voluntario'
    disponibilidad_id = Column(Integer, primary_key=True, autoincrement=True)
    voluntario_id = Column(Integer, ForeignKey('voluntario.voluntario_id'))
    dia = Column(Enum(DiaSemanaEnum), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    __table_args__ = (
        CheckConstraint('hora_fin > hora_inicio', name='chk_horas'),
        UniqueConstraint('voluntario_id', 'dia', 'hora_inicio', 'hora_fin', name='uq_disponibilidad'),
    )
    voluntario = relationship('Voluntario', back_populates='disponibilidades')

class Habilidad(Base):
    __tablename__ = 'habilidad'
    habilidad_id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)
    categoria = Column(String(50))
    voluntarios = relationship('VoluntarioHabilidad', back_populates='habilidad', cascade='all, delete-orphan')

class Recurso(Base):
    __tablename__ = 'recurso'
    recurso_id = Column(Integer, primary_key=True, autoincrement=True)
    campana_id = Column(Integer, ForeignKey('campana.campana_id'), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    cantidad_requerida = Column(Integer, CheckConstraint('cantidad_requerida > 0'), nullable=False)
    cantidad_actual = Column(Integer, CheckConstraint('cantidad_actual >= 0'), nullable=False, server_default=text('0'))
    unidad_medida = Column(String(20))
    campana = relationship('Campana', back_populates='recursos')

class VoluntarioActividad(Base):
    __tablename__ = 'voluntario_actividad'
    voluntario_id = Column(Integer, ForeignKey('voluntario.voluntario_id'), primary_key=True)
    actividad_id = Column(Integer, ForeignKey('actividad.actividad_id'), primary_key=True)
    fecha_registro = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    horas_dedicadas = Column(Numeric(5, 2), server_default=text('0'))
    comentarios = Column(Text)
    estado = Column(String(20), server_default=text("'pendiente'"))
    voluntario = relationship('Voluntario', back_populates='actividades')
    actividad = relationship('Actividad', back_populates='voluntarios')

class VoluntarioHabilidad(Base):
    __tablename__ = 'voluntario_habilidad'
    voluntario_id = Column(Integer, ForeignKey('voluntario.voluntario_id'), primary_key=True)
    habilidad_id = Column(Integer, ForeignKey('habilidad.habilidad_id'), primary_key=True)
    nivel = Column(Enum(NivelHabilidadEnum), nullable=False, server_default=text("'básico'"))
    anios_experiencia = Column(Integer, CheckConstraint('anios_experiencia >= 0'))
    certificado = Column(Boolean, server_default=text('FALSE'))
    voluntario = relationship('Voluntario', back_populates='habilidades')
    habilidad = relationship('Habilidad', back_populates='voluntarios')

class EstadisticasCampana(Base):
    __tablename__ = 'estadisticas_campana'
    campana_id = Column(Integer, ForeignKey('campana.campana_id'), primary_key=True)
    monto_recaudado = Column(Numeric(12, 2), server_default=text('0'))
    porcentaje_meta = Column(Numeric(5, 2), server_default=text('0'))
    num_donaciones = Column(Integer, server_default=text('0'))
    num_voluntarios = Column(Integer, server_default=text('0'))
    ultima_actualizacion = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    campana = relationship('Campana', back_populates='estadisticas')

# Vista para reportes: total donado por campaña
class VistaDonacionesCampana(Base):
    __tablename__ = 'vista_donaciones_campana'
    __table_args__ = {'info': dict(is_view=True)}

    campana_id = Column(Integer, primary_key=True)
    nombre_campana = Column(String(100))
    monto_total = Column(Numeric(12, 2))
    num_donaciones = Column(Integer)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

# Nota: Esta clase asume que existe una vista SQL llamada 'vista_donaciones_campana' en la base de datos.
# Debes crearla en tu DDL.sql, por ejemplo:
# CREATE OR REPLACE VIEW vista_donaciones_campana AS
# SELECT c.campana_id, c.nombre AS nombre_campana, COALESCE(SUM(d.monto), 0) AS monto_total, COUNT(d.donacion_id) AS num_donaciones, c.fecha_inicio, c.fecha_fin
# FROM campana c
# LEFT JOIN donacion d ON d.campana_id = c.campana_id AND d.tipo = 'monetaria'
# GROUP BY c.campana_id, c.nombre, c.fecha_inicio, c.fecha_fin;
