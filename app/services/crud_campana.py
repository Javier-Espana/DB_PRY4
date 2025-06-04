from sqlalchemy.orm import Session
from models import Campana
from typing import Optional

def get_campanas(db: Session):
    return db.query(Campana).all()

def get_campana(db: Session, campana_id: int):
    return db.query(Campana).filter(Campana.campana_id == campana_id).first()

def create_campana(db: Session, data: dict):
    campana = Campana(**data)
    db.add(campana)
    db.commit()
    db.refresh(campana)
    return campana

def update_campana(db: Session, campana_id: int, data: dict):
    campana = get_campana(db, campana_id)
    if not campana:
        return None
    # Validate that organizacion_id is not None
    if "organizacion_id" in data and data["organizacion_id"] is None:
        raise ValueError("El campo 'organizacion_id' no puede ser nulo.")
    for key, value in data.items():
        setattr(campana, key, value)
    db.commit()
    db.refresh(campana)
    return campana

def delete_campana(db: Session, campana_id: int):
    campana = get_campana(db, campana_id)
    if not campana:
        return False
    db.delete(campana)
    db.commit()
    return True
