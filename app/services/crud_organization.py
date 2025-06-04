# services/crud_organizacion.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from models import Organizacion, Campana
from typing import List, Optional

def get_organizaciones(db: Session, skip: int = 0, limit: int = 100) -> List[Organizacion]:
    return db.query(Organizacion).offset(skip).limit(limit).all()

def get_organizacion(db: Session, organizacion_id: int) -> Optional[Organizacion]:
    return db.query(Organizacion).filter(Organizacion.organizacion_id == organizacion_id).first()

def create_organizacion(db: Session, organizacion_data: dict):
    try:
        # Ensure we're not trying to set the ID manually
        organizacion_data.pop('organizacion_id', None)
        
        db_organizacion = Organizacion(**organizacion_data)
        db.add(db_organizacion)
        db.commit()
        db.refresh(db_organizacion)
        return db_organizacion
    except IntegrityError as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e.orig):
            # Reset the sequence for the primary key
            db.execute(text("SELECT setval(pg_get_serial_sequence('organizacion', 'organizacion_id'), MAX(organizacion_id)) FROM organizacion;"))
            db.commit()
            raise ValueError("Duplicate key detected. Sequence reset. Please try again.")
        raise e
    except Exception as e:
        db.rollback()
        raise e

def update_organizacion(db: Session, organizacion_id: int, update_data: dict) -> Optional[Organizacion]:
    org = get_organizacion(db, organizacion_id)
    if org:
        for key, value in update_data.items():
            setattr(org, key, value)
        db.commit()
        db.refresh(org)
    return org

def delete_organizacion(db: Session, organizacion_id: int) -> bool:
    org = get_organizacion(db, organizacion_id)
    if not org:
        return False
    # Delete all related activities for each campaign
    from models import Actividad  # Import here to avoid circular import
    campanas = db.query(Campana).filter(Campana.organizacion_id == organizacion_id).all()
    for campana in campanas:
        actividades = db.query(Actividad).filter(Actividad.campana_id == campana.campana_id).all()
        for actividad in actividades:
            db.delete(actividad)
        db.delete(campana)
    db.delete(org)
    db.commit()
    return True