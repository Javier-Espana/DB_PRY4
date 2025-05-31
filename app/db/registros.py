from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
import uuid

# Configuración inicial
fake = Faker('es_ES')  # Español con datos regionales
Faker.seed(42)  # Para resultados reproducibles
random.seed(42)

# Conexión a la base de datos (solo para ORM, no necesitamos una real)
engine = create_engine('postgresql://user:password@localhost/dbname')
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

# Cargar las tablas (reflejar desde la base de datos)
metadata.reflect(bind=engine)

# Obtener referencias a todas las tablas
organizacion = metadata.tables['organizacion']
categoria = metadata.tables['categoria']
sede = metadata.tables['sede']
campana = metadata.tables['campana']
actividad = metadata.tables['actividad']
donante = metadata.tables['donante']
preferencia_contacto = metadata.tables['preferencia_contacto']
donacion = metadata.tables['donacion']
voluntario = metadata.tables['voluntario']
disponibilidad_voluntario = metadata.tables['disponibilidad_voluntario']
habilidad = metadata.tables['habilidad']
recurso = metadata.tables['recurso']
voluntario_actividad = metadata.tables['voluntario_actividad']
voluntario_habilidad = metadata.tables['voluntario_habilidad']
estadisticas_campana = metadata.tables['estadisticas_campana']

# Lista para almacenar todas las sentencias SQL
insert_queries = []

def generar_datos():
    # 1. Organizaciones (10-15)
    org_ids = []
    for _ in range(random.randint(10, 15)):
        org_data = {
            'nombre': fake.company(),
            'descripcion': fake.paragraph(),
            'email': fake.company_email(),
            'telefono': fake.phone_number(),
            'direccion': fake.address().replace('\n', ', '),
            'sitio_web': fake.url(),
            'fecha_registro': fake.date_between(start_date='-5y', end_date='today'),
            'activa': random.choice([True, False])
        }
        insert_queries.append(f"""
        INSERT INTO organizacion (nombre, descripcion, email, telefono, direccion, sitio_web, fecha_registro, activa)
        VALUES ('{org_data['nombre']}', '{org_data['descripcion']}', '{org_data['email']}', 
                '{org_data['telefono']}', '{org_data['direccion']}', '{org_data['sitio_web']}', 
                '{org_data['fecha_registro']}', {org_data['activa']});
        """)
        org_ids.append(f"(SELECT organizacion_id FROM organizacion WHERE email = '{org_data['email']}')")

    # 2. Categorías (5-8)
    cat_ids = []
    categorias = ['Medio Ambiente', 'Educación', 'Salud', 'Animales', 'Derechos Humanos', 'Arte y Cultura', 'Desarrollo Comunitario']
    for cat in categorias[:random.randint(5, 8)]:
        insert_queries.append(f"""
        INSERT INTO categoria (nombre, descripcion)
        VALUES ('{cat}', '{fake.sentence()}');
        """)
        cat_ids.append(f"(SELECT categoria_id FROM categoria WHERE nombre = '{cat}')")

    # 3. Sedes (3-5 por organización)
    sede_ids = []
    for org_id in org_ids:
        for _ in range(random.randint(3, 5)):
            sede_data = {
                'nombre': fake.street_name() + " Office",
                'direccion': fake.address().replace('\n', ', '),
                'ciudad': fake.city(),
                'region': fake.state(),
                'codigo_postal': fake.postcode(),
                'telefono': fake.phone_number(),
                'email': fake.company_email(),
                'horario_apertura': f"{random.randint(7, 9)}:00:00",
                'horario_cierre': f"{random.randint(17, 21)}:00:00"
            }
            insert_queries.append(f"""
            INSERT INTO sede (nombre, direccion, ciudad, region, codigo_postal, telefono, email, horario_apertura, horario_cierre)
            VALUES ('{sede_data['nombre']}', '{sede_data['direccion']}', '{sede_data['ciudad']}', 
                    '{sede_data['region']}', '{sede_data['codigo_postal']}', '{sede_data['telefono']}', 
                    '{sede_data['email']}', '{sede_data['horario_apertura']}', '{sede_data['horario_cierre']}');
            """)
            sede_ids.append(f"(SELECT sede_id FROM sede WHERE email = '{sede_data['email']}')")

    # 4. Campañas (3-8 por organización)
    campana_ids = []
    estados = ['planificada', 'activa', 'pausada', 'finalizada']
    for org_id in org_ids:
        for _ in range(random.randint(3, 8)):
            fecha_inicio = fake.date_between(start_date='-1y', end_date='+1y')
            fecha_fin = fecha_inicio + timedelta(days=random.randint(30, 180)) if random.random() > 0.3 else None
            campana_data = {
                'organizacion_id': org_id,
                'categoria_id': random.choice(cat_ids) if random.random() > 0.2 else 'NULL',
                'sede_principal_id': random.choice(sede_ids) if random.random() > 0.3 else 'NULL',
                'nombre': fake.catch_phrase(),
                'descripcion': '\n'.join(fake.paragraphs(2)),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'meta_monetaria': round(random.uniform(1000, 50000), 2),
                'estado': random.choice(estados)
            }
            insert_queries.append(f"""
            INSERT INTO campana (organizacion_id, categoria_id, sede_principal_id, nombre, descripcion, 
                                fecha_inicio, fecha_fin, meta_monetaria, estado)
            VALUES ({campana_data['organizacion_id']}, {campana_data['categoria_id']}, {campana_data['sede_principal_id']}, 
                    '{campana_data['nombre']}', '{campana_data['descripcion']}', 
                    '{campana_data['fecha_inicio']}', {f"'{campana_data['fecha_fin']}'" if campana_data['fecha_fin'] else 'NULL'}, 
                    {campana_data['meta_monetaria']}, '{campana_data['estado']}');
            """)
            campana_ids.append(f"(SELECT campana_id FROM campana WHERE nombre = '{campana_data['nombre']}')")

    # 5. Actividades (5-15 por campaña)
    actividad_ids = []
    for camp_id in campana_ids:
        for _ in range(random.randint(5, 15)):
            fecha_inicio = fake.date_time_between(start_date='-1y', end_date='+1y')
            fecha_fin = fecha_inicio + timedelta(hours=random.randint(2, 8))
            actividad_data = {
                'campana_id': camp_id,
                'sede_id': random.choice(sede_ids) if random.random() > 0.2 else 'NULL',
                'nombre': fake.bs(),
                'descripcion': fake.paragraph(),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'capacidad_max': random.randint(10, 100)
            }
            insert_queries.append(f"""
            INSERT INTO actividad (campana_id, sede_id, nombre, descripcion, fecha_inicio, fecha_fin, capacidad_max)
            VALUES ({actividad_data['campana_id']}, {actividad_data['sede_id']}, 
                    '{actividad_data['nombre']}', '{actividad_data['descripcion']}', 
                    '{actividad_data['fecha_inicio']}', '{actividad_data['fecha_fin']}', 
                    {actividad_data['capacidad_max']});
            """)
            actividad_ids.append(f"(SELECT actividad_id FROM actividad WHERE nombre = '{actividad_data['nombre']}')")

    # 6. Donantes (100-150 individuales, 30-50 empresas)
    donante_ids = []
    for _ in range(random.randint(100, 150)):
        donante_data = {
            'tipo': 'individual',
            'nombre': fake.first_name(),
            'apellido': fake.last_name(),
            'empresa': 'NULL',
            'email': fake.email(),
            'telefono': fake.phone_number(),
            'direccion': fake.address().replace('\n', ', '),
            'fecha_registro': fake.date_between(start_date='-3y', end_date='today')
        }
        insert_queries.append(f"""
        INSERT INTO donante (tipo, nombre, apellido, empresa, email, telefono, direccion, fecha_registro)
        VALUES ('{donante_data['tipo']}', '{donante_data['nombre']}', '{donante_data['apellido']}', 
                {donante_data['empresa']}, '{donante_data['email']}', '{donante_data['telefono']}', 
                '{donante_data['direccion']}', '{donante_data['fecha_registro']}');
        """)
        donante_ids.append(f"(SELECT donante_id FROM donante WHERE email = '{donante_data['email']}')")

    for _ in range(random.randint(30, 50)):
        donante_data = {
            'tipo': 'empresa',
            'nombre': 'NULL',
            'apellido': 'NULL',
            'empresa': fake.company(),
            'email': fake.company_email(),
            'telefono': fake.phone_number(),
            'direccion': fake.address().replace('\n', ', '),
            'fecha_registro': fake.date_between(start_date='-3y', end_date='today')
        }
        insert_queries.append(f"""
        INSERT INTO donante (tipo, nombre, apellido, empresa, email, telefono, direccion, fecha_registro)
        VALUES ('{donante_data['tipo']}', {donante_data['nombre']}, {donante_data['apellido']}, 
                '{donante_data['empresa']}', '{donante_data['email']}', '{donante_data['telefono']}', 
                '{donante_data['direccion']}', '{donante_data['fecha_registro']}');
        """)
        donante_ids.append(f"(SELECT donante_id FROM donante WHERE email = '{donante_data['email']}')")

    # 7. Preferencias de contacto (2-5 por donante)
    tipos_contacto = ['email', 'teléfono', 'correo', 'sms', 'whatsapp']
    for don_id in donante_ids:
        for _ in range(random.randint(2, 5)):
            tipo = random.choice(tipos_contacto)
            permitido = random.choice([True, False])
            insert_queries.append(f"""
            INSERT INTO preferencia_contacto (donante_id, tipo, permitido)
            VALUES ({don_id}, '{tipo}', {permitido});
            """)

    # 8. Donaciones (5-20 por donante)
    for don_id in donante_ids:
        for _ in range(random.randint(5, 20)):
            tipo = random.choice(['monetaria', 'especie'])
            camp_id = random.choice(campana_ids)
            if tipo == 'monetaria':
                monto = round(random.uniform(10, 5000), 2)
                desc_especie = 'NULL'
            else:
                monto = 'NULL'
                desc_especie = f"'{fake.sentence()}'"
            
            donacion_data = {
                'donante_id': don_id,
                'campana_id': camp_id,
                'tipo': tipo,
                'monto': monto,
                'descripcion_especie': desc_especie,
                'fecha': fake.date_time_between(start_date='-2y', end_date='now'),
                'anonima': random.choice([True, False]),
                'mensaje': fake.sentence() if random.random() > 0.7 else 'NULL'
            }
            insert_queries.append(f"""
            INSERT INTO donacion (donante_id, campana_id, tipo, monto, descripcion_especie, fecha, anonima, mensaje)
            VALUES ({donacion_data['donante_id']}, {donacion_data['campana_id']}, '{donacion_data['tipo']}', 
                    {donacion_data['monto']}, {donacion_data['descripcion_especie']}, 
                    '{donacion_data['fecha']}', {donacion_data['anonima']}, 
                    {f"'{donacion_data['mensaje']}'" if donacion_data['mensaje'] != 'NULL' else 'NULL'});
            """)

    # 9. Voluntarios (50-100)
    voluntario_ids = []
    for _ in range(random.randint(50, 100)):
        fecha_nac = fake.date_of_birth(minimum_age=16, maximum_age=80)
        voluntario_data = {
            'nombre': fake.first_name(),
            'apellido': fake.last_name(),
            'email': fake.email(),
            'telefono': fake.phone_number(),
            'direccion': fake.address().replace('\n', ', '),
            'fecha_nacimiento': fecha_nac,
            'fecha_registro': fake.date_between(start_date=fecha_nac + timedelta(days=16*365), end_date='today'),
            'activo': random.choice([True, False])
        }
        insert_queries.append(f"""
        INSERT INTO voluntario (nombre, apellido, email, telefono, direccion, fecha_nacimiento, fecha_registro, activo)
        VALUES ('{voluntario_data['nombre']}', '{voluntario_data['apellido']}', 
                '{voluntario_data['email']}', '{voluntario_data['telefono']}', 
                '{voluntario_data['direccion']}', '{voluntario_data['fecha_nacimiento']}', 
                '{voluntario_data['fecha_registro']}', {voluntario_data['activo']});
        """)
        voluntario_ids.append(f"(SELECT voluntario_id FROM voluntario WHERE email = '{voluntario_data['email']}')")

    # 10. Disponibilidad voluntarios (2-5 por voluntario)
    dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    for vol_id in voluntario_ids:
        for _ in range(random.randint(2, 5)):
            dia = random.choice(dias_semana)
            hora_inicio = f"{random.randint(8, 12)}:00:00"
            hora_fin = f"{random.randint(13, 20)}:00:00"
            insert_queries.append(f"""
            INSERT INTO disponibilidad_voluntario (voluntario_id, dia, hora_inicio, hora_fin)
            VALUES ({vol_id}, '{dia}', '{hora_inicio}', '{hora_fin}');
            """)

    # 11. Habilidades (10-15)
    habilidad_ids = []
    habilidades = [
        'Idiomas', 'Primeros Auxilios', 'Carpintería', 'Programación',
        'Diseño Gráfico', 'Enseñanza', 'Cocina', 'Jardinería',
        'Construcción', 'Traducción', 'Música', 'Fotografía',
        'Redes Sociales', 'Contabilidad', 'Medicina'
    ]
    for hab in habilidades[:random.randint(10, 15)]:
        insert_queries.append(f"""
        INSERT INTO habilidad (nombre, descripcion, categoria)
        VALUES ('{hab}', '{fake.sentence()}', '{random.choice(categorias[:len(cat_ids)])}');
        """)
        habilidad_ids.append(f"(SELECT habilidad_id FROM habilidad WHERE nombre = '{hab}')")

    # 12. Voluntario-Habilidad (1-4 por voluntario)
    niveles = ['básico', 'intermedio', 'avanzado']
    for vol_id in voluntario_ids:
        habilidades_vol = random.sample(habilidad_ids, k=random.randint(1, 4))
        for hab_id in habilidades_vol:
            insert_queries.append(f"""
            INSERT INTO voluntario_habilidad (voluntario_id, habilidad_id, nivel, anios_experiencia, certificado)
            VALUES ({vol_id}, {hab_id}, '{random.choice(niveles)}', 
                    {random.randint(0, 10)}, {random.choice([True, False])});
            """)

    # 13. Recursos (3-10 por campaña)
    recursos = ['Alimentos', 'Ropa', 'Medicinas', 'Material Escolar', 'Herramientas', 'Equipos Electrónicos', 'Libros']
    for camp_id in campana_ids:
        for _ in range(random.randint(3, 10)):
            recurso_data = {
                'campana_id': camp_id,
                'nombre': random.choice(recursos),
                'descripcion': fake.sentence(),
                'cantidad_requerida': random.randint(10, 500),
                'cantidad_actual': random.randint(0, 500),
                'unidad_medida': random.choice(['kg', 'unidades', 'litros', 'paquetes', 'cajas'])
            }
            insert_queries.append(f"""
            INSERT INTO recurso (campana_id, nombre, descripcion, cantidad_requerida, cantidad_actual, unidad_medida)
            VALUES ({recurso_data['campana_id']}, '{recurso_data['nombre']}', '{recurso_data['descripcion']}', 
                    {recurso_data['cantidad_requerida']}, {recurso_data['cantidad_actual']}, 
                    '{recurso_data['unidad_medida']}');
            """)

    # 14. Voluntario-Actividad (3-10 por actividad)
    for act_id in actividad_ids:
        voluntarios_act = random.sample(voluntario_ids, k=random.randint(3, min(10, len(voluntario_ids))))
        for vol_id in voluntarios_act:
            insert_queries.append(f"""
            INSERT INTO voluntario_actividad (voluntario_id, actividad_id, horas_dedicadas, comentarios, estado)
            VALUES ({vol_id}, {act_id}, {round(random.uniform(1, 20), 2)}, 
                    '{fake.sentence() if random.random() > 0.5 else 'NULL'}', 
                    '{random.choice(['pendiente', 'confirmado', 'completado', 'cancelado'])}');
            """)

    # 15. Estadísticas (generadas automáticamente por triggers)

    # Escribir a archivo
    with open('Registros.sql', 'w', encoding='utf-8') as f:
        f.write('-- Datos de prueba generados automáticamente\n')
        f.write('-- Total de registros: ' + str(len(insert_queries)) + '\n\n')
        f.write('BEGIN;\n\n')
        f.write('\n'.join(insert_queries))
        f.write('\n\nCOMMIT;\n')

    print(f"Archivo Registros.sql generado con {len(insert_queries)} sentencias INSERT!")

if __name__ == '__main__':
    generar_datos()