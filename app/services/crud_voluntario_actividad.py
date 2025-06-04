from sqlalchemy.orm import Session
from models import VoluntarioActividad
from typing import Optional

def get_voluntario_actividades(db: Session, actividad_id: Optional[int] = None, voluntario_id: Optional[int] = None):
    query = db.query(VoluntarioActividad)
    if actividad_id:
        query = query.filter(VoluntarioActividad.actividad_id == actividad_id)
    if voluntario_id:
        query = query.filter(VoluntarioActividad.voluntario_id == voluntario_id)
    return query.all()

def get_voluntario_actividad(db: Session, voluntario_id: int, actividad_id: int):
    return db.query(VoluntarioActividad).filter(
        VoluntarioActividad.voluntario_id == voluntario_id,
        VoluntarioActividad.actividad_id == actividad_id
    ).first()

def create_voluntario_actividad(db: Session, data: dict):
    va = VoluntarioActividad(**data)
    db.add(va)
    db.commit()
    db.refresh(va)
    return va

def update_voluntario_actividad(db: Session, voluntario_id: int, actividad_id: int, data: dict):
    va = get_voluntario_actividad(db, voluntario_id, actividad_id)
    if not va:
        return None
    for key, value in data.items():
        setattr(va, key, value)
    db.commit()
    db.refresh(va)
    return va

def delete_voluntario_actividad(db: Session, voluntario_id: int, actividad_id: int):
    va = get_voluntario_actividad(db, voluntario_id, actividad_id)
    if not va:
        return False
    db.delete(va)
    db.commit()
    return True
