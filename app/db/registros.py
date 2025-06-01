from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Boolean, Date, Time, Numeric, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración inicial
fake = Faker('es_ES')
Faker.seed(42)
random.seed(42)

# --- Modelos ORM locales (sin conexión a BD) ---
Base = declarative_base()

class Organizacion(Base):
    __tablename__ = 'organizacion'
    organizacion_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    email = Column(String(100), nullable=False, unique=True)
    telefono = Column(String(20))
    direccion = Column(Text)
    sitio_web = Column(String(100))
    fecha_registro = Column(Date, nullable=False, server_default='CURRENT_DATE')
    activa = Column(Boolean, server_default='TRUE')

class Categoria(Base):
    __tablename__ = 'categoria'
    categoria_id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)

class Sede(Base):
    __tablename__ = 'sede'
    sede_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(50), nullable=False)
    region = Column(String(50))
    codigo_postal = Column(String(10))
    telefono = Column(String(20))
    email = Column(String(100))
    horario_apertura = Column(Time)
    horario_cierre = Column(Time)

class Campana(Base):
    __tablename__ = 'campana'
    campana_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    meta_monetaria = Column(Numeric)
    estado = Column(String(20))
    organizacion_id = Column(Integer)
    categoria_id = Column(Integer)
    sede_principal_id = Column(Integer)

# --- Función para generar INSERTs desde modelos ORM ---
def generar_inserts_sql():
    inserts = []
    total_registros = 0
    # Organizaciones
    org_ids = []
    num_orgs = random.randint(20, 30)
    for i in range(1, num_orgs+1):
        org = Organizacion(
            nombre=fake.company(),
            descripcion=fake.paragraph(),
            email=fake.company_email(),
            telefono=fake.phone_number(),
            direccion=fake.address().replace('\n', ', '),
            sitio_web=fake.url(),
            fecha_registro=fake.date_between(start_date='-5y', end_date='today'),
            activa=random.choice([True, False])
        )
        inserts.append(
            f"INSERT INTO organizacion (organizacion_id, nombre, descripcion, email, telefono, direccion, sitio_web, fecha_registro, activa) "
            f"VALUES ({i}, '{org.nombre}', '{org.descripcion}', '{org.email}', '{org.telefono}', "
            f"'{org.direccion}', '{org.sitio_web}', '{org.fecha_registro}', {org.activa});"
        )
        org_ids.append(i)
        total_registros += 1
    # Categorías (garantizar unicidad)
    cat_ids = []
    categorias = ['Medio Ambiente', 'Educación', 'Salud', 'Animales', 'Derechos Humanos', 'Arte y Cultura', 'Desarrollo Comunitario']
    random.shuffle(categorias)
    num_cats = min(random.randint(7, 10), len(categorias))
    categorias_unicas = categorias[:num_cats]
    for j, cat in enumerate(categorias_unicas, 1):
        inserts.append(f"INSERT INTO categoria (categoria_id, nombre, descripcion) VALUES ({j}, '{cat}', '{fake.sentence()}');")
        cat_ids.append(j)
        total_registros += 1
    # Sedes (5-10 por organización)
    sede_ids = []
    sede_id_counter = 1
    for org_id in org_ids:
        for _ in range(random.randint(5, 10)):
            nombre = fake.company() + " Sede"
            direccion = fake.address().replace('\n', ', ')
            ciudad = fake.city()
            region = fake.state()
            codigo_postal = fake.postcode()
            telefono = fake.phone_number()
            email = fake.company_email()
            horario_apertura = '08:00:00'
            horario_cierre = '17:00:00'
            inserts.append(
                f"INSERT INTO sede (sede_id, nombre, direccion, ciudad, region, codigo_postal, telefono, email, horario_apertura, horario_cierre) "
                f"VALUES ({sede_id_counter}, '{nombre}', '{direccion}', '{ciudad}', '{region}', '{codigo_postal}', '{telefono}', '{email}', '{horario_apertura}', '{horario_cierre}');"
            )
            sede_ids.append(sede_id_counter)
            sede_id_counter += 1
            total_registros += 1
    # Campañas (10-20 por organización)
    campana_id_counter = 1
    for org_id in org_ids:
        for _ in range(random.randint(10, 20)):
            nombre = fake.catch_phrase()
            descripcion = fake.paragraph()
            fecha_inicio = fake.date_between(start_date='-3y', end_date='today')
            fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 180))
            meta_monetaria = random.randint(1000, 10000)
            estado = random.choice(['planificada', 'activa', 'pausada', 'finalizada'])
            categoria_id = random.choice(cat_ids)
            sede_principal_id = random.choice(sede_ids)
            inserts.append(
                f"INSERT INTO campana (campana_id, nombre, descripcion, fecha_inicio, fecha_fin, meta_monetaria, estado, organizacion_id, categoria_id, sede_principal_id) "
                f"VALUES ({campana_id_counter}, '{nombre}', '{descripcion}', '{fecha_inicio}', '{fecha_fin}', {meta_monetaria}, '{estado}', {org_id}, {categoria_id}, {sede_principal_id});"
            )
            campana_id_counter += 1
            total_registros += 1
    # Donantes (200-300 individuales, 80-120 empresas)
    donante_id_counter = 1
    for _ in range(random.randint(200, 300)):
        nombre = fake.first_name()
        apellido = fake.last_name()
        email = fake.email()
        tipo = 'individual'
        inserts.append(
            f"INSERT INTO donante (donante_id, tipo, nombre, apellido, email) VALUES ({donante_id_counter}, '{tipo}', '{nombre}', '{apellido}', '{email}');"
        )
        donante_id_counter += 1
        total_registros += 1
    for _ in range(random.randint(80, 120)):
        empresa = fake.company()
        email = fake.company_email()
        tipo = 'empresa'
        inserts.append(
            f"INSERT INTO donante (donante_id, tipo, empresa, email) VALUES ({donante_id_counter}, '{tipo}', '{empresa}', '{email}');"
        )
        donante_id_counter += 1
        total_registros += 1
    # Voluntarios (200-300)
    voluntario_id_counter = 1
    for _ in range(random.randint(200, 300)):
        nombre = fake.first_name()
        apellido = fake.last_name()
        email = fake.email()
        fecha_nacimiento = fake.date_of_birth(minimum_age=18, maximum_age=65)
        inserts.append(
            f"INSERT INTO voluntario (voluntario_id, nombre, apellido, email, fecha_nacimiento) VALUES ({voluntario_id_counter}, '{nombre}', '{apellido}', '{email}', '{fecha_nacimiento}');"
        )
        voluntario_id_counter += 1
        total_registros += 1
    # Donaciones (600-900)
    donacion_id_counter = 1
    for _ in range(random.randint(600, 900)):
        campana_id = random.randint(1, campana_id_counter-1)
        donante_id = random.randint(1, donante_id_counter-1)
        tipo = random.choice(['monetaria', 'especie'])
        if tipo == 'monetaria':
            monto = round(random.uniform(10, 1000), 2)
            descripcion_especie = 'NULL'
        else:
            monto = 'NULL'
            desc = f"{fake.word().capitalize()} {fake.word()} {fake.word()}".replace("'", "''")
            descripcion_especie = f"'{desc}'"
        fecha = fake.date_between(start_date='-2y', end_date='today')
        # Asegurar que el campo tipo siempre esté presente en el insert
        inserts.append(
            f"INSERT INTO donacion (donacion_id, campana_id, donante_id, tipo, monto, descripcion_especie, fecha) VALUES ({donacion_id_counter}, {campana_id}, {donante_id}, '{tipo}', {monto}, {descripcion_especie}, '{fecha}');"
        )
        donacion_id_counter += 1
        total_registros += 1
    # Habilidad (10-20)
    habilidad_id_counter = 1
    habilidades = ['Liderazgo', 'Comunicación', 'Organización', 'Trabajo en equipo', 'Gestión de proyectos', 'Creatividad', 'Resolución de problemas', 'Empatía', 'Negociación', 'Planificación', 'Análisis', 'Adaptabilidad']
    for nombre in habilidades[:random.randint(10, 12)]:
        inserts.append(
            f"INSERT INTO habilidad (habilidad_id, nombre) VALUES ({habilidad_id_counter}, '{nombre}');"
        )
        habilidad_id_counter += 1
        total_registros += 1
    # Recurso (100-200)
    recurso_id_counter = 1
    for _ in range(random.randint(100, 200)):
        campana_id = random.randint(1, campana_id_counter-1)
        nombre = fake.word().capitalize()
        cantidad = random.randint(1, 100)
        inserts.append(
            f"INSERT INTO recurso (recurso_id, campana_id, nombre, cantidad) VALUES ({recurso_id_counter}, {campana_id}, '{nombre}', {cantidad});"
        )
        recurso_id_counter += 1
        total_registros += 1
    # Actividad (200-400)
    actividad_id_counter = 1
    for campana_id in range(1, campana_id_counter):
        for _ in range(random.randint(2, 4)):
            nombre = fake.bs().capitalize()
            sede_id = random.choice(sede_ids)
            fecha_inicio = fake.date_between(start_date='-2y', end_date='today')
            fecha_fin = fecha_inicio + timedelta(days=random.randint(1, 10))
            inserts.append(
                f"INSERT INTO actividad (actividad_id, campana_id, nombre, sede_id, fecha_inicio, fecha_fin) VALUES ({actividad_id_counter}, {campana_id}, '{nombre}', {sede_id}, '{fecha_inicio}', '{fecha_fin}');"
            )
            actividad_id_counter += 1
            total_registros += 1
    # Voluntario_Actividad (300-600)
    for voluntario_id in range(1, voluntario_id_counter):
        for _ in range(random.randint(1, 2)):
            actividad_id = random.randint(1, actividad_id_counter-1)
            inserts.append(
                f"INSERT INTO voluntario_actividad (voluntario_id, actividad_id) VALUES ({voluntario_id}, {actividad_id});"
            )
            total_registros += 1
    # Voluntario_Habilidad (300-600)
    for voluntario_id in range(1, voluntario_id_counter):
        habilidades_asignadas = random.sample(range(1, habilidad_id_counter), random.randint(1, 2))
        for habilidad_id in habilidades_asignadas:
            inserts.append(
                f"INSERT INTO voluntario_habilidad (voluntario_id, habilidad_id) VALUES ({voluntario_id}, {habilidad_id});"
            )
            total_registros += 1
    # Disponibilidad_Voluntario (300-600)
    disponibilidad_id_counter = 1
    dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    for voluntario_id in range(1, voluntario_id_counter):
        for _ in range(random.randint(1, 2)):
            dia = random.choice(dias_semana)
            hora_inicio = f"{random.randint(7, 12)}:00:00"
            hora_fin = f"{random.randint(13, 20)}:00:00"
            inserts.append(
                f"INSERT INTO disponibilidad_voluntario (disponibilidad_id, voluntario_id, dia, hora_inicio, hora_fin) VALUES ({disponibilidad_id_counter}, {voluntario_id}, '{dia}', '{hora_inicio}', '{hora_fin}');"
            )
            disponibilidad_id_counter += 1
            total_registros += 1
    # Preferencia_Contacto (200-400)
    preferencia_id_counter = 1
    tipos_contacto = ['email', 'teléfono', 'correo', 'sms', 'whatsapp']
    for donante_id in range(1, donante_id_counter):
        tipo = random.choice(tipos_contacto)
        valor = fake.phone_number() if tipo != 'email' else fake.email()
        inserts.append(
            f"INSERT INTO preferencia_contacto (preferencia_id, donante_id, tipo, valor) VALUES ({preferencia_id_counter}, {donante_id}, '{tipo}', '{valor}');"
        )
        preferencia_id_counter += 1
        total_registros += 1
    # Estadisticas_Campana (1 por campaña)
    for campana_id in range(1, campana_id_counter):
        total_donaciones = random.randint(0, 100)
        monto_total = round(random.uniform(0, 10000), 2)
        inserts.append(
            f"INSERT INTO estadisticas_campana (campana_id, total_donaciones, monto_total) VALUES ({campana_id}, {total_donaciones}, {monto_total});"
        )
        total_registros += 1
    # Escribir archivo
    os.makedirs("/database", exist_ok=True)
    with open("/database/Registros.sql", "w", encoding="utf-8") as f:
        f.write("-- Datos generados automáticamente con ORM (sin conexión a BD)\n")
        f.write("\n".join(inserts))
    print(f"Archivo Registros.sql generado con {len(inserts)} INSERTs y {total_registros} registros distribuidos.")

if __name__ == '__main__':
    generar_inserts_sql()