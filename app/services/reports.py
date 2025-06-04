# services/reports.py
from sqlalchemy.orm import Session
from models import Donacion, Campana, Voluntario, VoluntarioActividad, Donante
from sqlalchemy import func, and_, or_
import datetime

def get_donaciones_por_campana(db: Session, fecha_inicio=None, fecha_fin=None, monto_minimo=None, monto_maximo=None):
    query = db.query(
        Campana.campana_id,
        Campana.nombre.label('campana'),
        func.sum(Donacion.monto).label('monto_total'),
        func.count(Donacion.donacion_id).label('num_donaciones')
    ).join(Donacion, Donacion.campana_id == Campana.campana_id)
    if fecha_inicio:
        query = query.filter(Donacion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Donacion.fecha <= fecha_fin)
    if monto_minimo is not None:
        query = query.filter(Donacion.monto >= monto_minimo)
    if monto_maximo is not None:
        query = query.filter(Donacion.monto <= monto_maximo)
    query = query.group_by(Campana.campana_id, Campana.nombre)
    result = query.all()
    return [
        {
            'campana_id': r.campana_id,
            'campana': r.campana,
            'monto_total': float(r.monto_total or 0),
            'num_donaciones': r.num_donaciones
        }
        for r in result
    ]

def get_voluntarios_por_actividad(db: Session, fecha_inicio=None, fecha_fin=None, edad_minima=None, edad_maxima=None):
    # Suponiendo que VoluntarioActividad tiene fecha y Voluntario tiene edad
    query = db.query(
        VoluntarioActividad.actividad_id,
        func.count(VoluntarioActividad.voluntario_id).label('num_voluntarios')
    ).join(Voluntario, Voluntario.voluntario_id == VoluntarioActividad.voluntario_id)
    if fecha_inicio:
        query = query.filter(VoluntarioActividad.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(VoluntarioActividad.fecha <= fecha_fin)
    if edad_minima is not None:
        query = query.filter(Voluntario.edad >= edad_minima)
    if edad_maxima is not None:
        query = query.filter(Voluntario.edad <= edad_maxima)
    query = query.group_by(VoluntarioActividad.actividad_id)
    result = query.all()
    return [
        {
            'actividad_id': r.actividad_id,
            'num_voluntarios': r.num_voluntarios
        }
        for r in result
    ]

def get_donaciones_por_donante(db: Session, fecha_inicio=None, fecha_fin=None, monto_minimo=None, monto_maximo=None):
    query = db.query(
        Donante.donante_id,
        Donante.nombre,
        Donante.apellido,
        func.sum(Donacion.monto).label('monto_total'),
        func.count(Donacion.donacion_id).label('num_donaciones')
    ).join(Donacion, Donacion.donante_id == Donante.donante_id)
    if fecha_inicio:
        query = query.filter(Donacion.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Donacion.fecha <= fecha_fin)
    if monto_minimo is not None:
        query = query.filter(Donacion.monto >= monto_minimo)
    if monto_maximo is not None:
        query = query.filter(Donacion.monto <= monto_maximo)
    query = query.group_by(Donante.donante_id, Donante.nombre, Donante.apellido)
    result = query.all()
    return [
        {
            'donante_id': r.donante_id,
            'nombre': r.nombre,
            'apellido': r.apellido,
            'monto_total': float(r.monto_total or 0),
            'num_donaciones': r.num_donaciones
        }
        for r in result
    ]

def get_distribucion_voluntarios_por_edad(db: Session, edad_minima=None, edad_maxima=None):
    query = db.query(
        Voluntario.edad,
        func.count(Voluntario.voluntario_id).label('num_voluntarios')
    )
    if edad_minima is not None:
        query = query.filter(Voluntario.edad >= edad_minima)
    if edad_maxima is not None:
        query = query.filter(Voluntario.edad <= edad_maxima)
    query = query.group_by(Voluntario.edad).order_by(Voluntario.edad)
    result = query.all()
    return [
        {
            'edad': r.edad,
            'num_voluntarios': r.num_voluntarios
        }
        for r in result
    ]

def get_efectividad_campanas(db: Session, fecha_inicio=None, fecha_fin=None, estado=None):
    query = db.query(
        Campana.campana_id,
        Campana.nombre,
        Campana.meta_monetaria,
        func.coalesce(func.sum(Donacion.monto), 0).label('monto_recaudado'),
        ((func.coalesce(func.sum(Donacion.monto), 0) / func.nullif(Campana.meta_monetaria, 0)) * 100).label('porcentaje_cumplimiento'),
        Campana.estado
    ).outerjoin(Donacion, Donacion.campana_id == Campana.campana_id)
    if fecha_inicio:
        query = query.filter(Campana.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Campana.fecha_fin <= fecha_fin)
    if estado and estado != 'Todos':
        query = query.filter(Campana.estado == estado)
    query = query.group_by(Campana.campana_id, Campana.nombre, Campana.meta_monetaria, Campana.estado)
    result = query.all()
    return [
        {
            'campana_id': r.campana_id,
            'nombre': r.nombre,
            'meta_monetaria': float(r.meta_monetaria or 0),
            'monto_recaudado': float(r.monto_recaudado or 0),
            'porcentaje_cumplimiento': float(r.porcentaje_cumplimiento or 0),
            'estado': r.estado
        }
        for r in result
    ]
