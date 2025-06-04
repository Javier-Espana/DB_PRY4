from sqlalchemy.orm import Session
from models import Donacion
from typing import Optional

def get_donaciones(db: Session, campana_id: Optional[int] = None):
    query = db.query(Donacion)
    if campana_id:
        query = query.filter(Donacion.campana_id == campana_id)
    return query.all()

def get_donacion(db: Session, donacion_id: int):
    return db.query(Donacion).filter(Donacion.donacion_id == donacion_id).first()

def create_donacion(db: Session, data: dict):
    donacion = Donacion(**data)
    db.add(donacion)
    db.commit()
    db.refresh(donacion)
    return donacion

def update_donacion(db: Session, donacion_id: int, data: dict):
    donacion = get_donacion(db, donacion_id)
    if not donacion:
        return None
    for key, value in data.items():
        setattr(donacion, key, value)
    db.commit()
    db.refresh(donacion)
    return donacion

def delete_donacion(db: Session, donacion_id: int):
    donacion = get_donacion(db, donacion_id)
    if not donacion:
        return False
    db.delete(donacion)
    db.commit()
    return True
