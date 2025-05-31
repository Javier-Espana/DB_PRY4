# services/crud_organizacion.py
from sqlalchemy.orm import Session
from models import Organizacion
from typing import List, Optional

def get_organizaciones(db: Session, skip: int = 0, limit: int = 100) -> List[Organizacion]:
    return db.query(Organizacion).offset(skip).limit(limit).all()

def get_organizacion(db: Session, organizacion_id: int) -> Optional[Organizacion]:
    return db.query(Organizacion).filter(Organizacion.organizacion_id == organizacion_id).first()

def create_organizacion(db: Session, organizacion_data: dict) -> Organizacion:
    org = Organizacion(**organizacion_data)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

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
    if org:
        db.delete(org)
        db.commit()
        return True
    return False