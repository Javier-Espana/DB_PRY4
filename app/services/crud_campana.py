from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
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
    try:
        # Get the campaign first
        campana = get_campana(db, campana_id)
        if not campana:
            return False
            
        # First try to set organizacion_id to NULL if there are dependencies
        db.execute(
            text("UPDATE campana SET organizacion_id = NULL WHERE campana_id = :campana_id"),
            {"campana_id": campana_id}
        )
        
        # Then delete the campaign
        db.delete(campana)
        db.commit()
        return True
        
    except IntegrityError as e:
        db.rollback()
        # If there are still dependencies, we need to handle them
        if "foreign key violation" in str(e.orig).lower():
            raise ValueError("No se puede eliminar la campaña porque tiene donaciones u otras dependencias asociadas")
        raise ValueError(f"Error de integridad al eliminar la campaña: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al eliminar la campaña: {str(e)}")
