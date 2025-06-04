from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from models import Donante

def get_donantes(db: Session):
    return db.query(Donante).all()

def get_donante(db: Session, donante_id: int):
    return db.query(Donante).filter(Donante.donante_id == donante_id).first()

def create_donante(db: Session, data: dict):
    try:
        # No permitir setear donante_id manualmente
        data.pop('donante_id', None)
        donante = Donante(**data)
        db.add(donante)
        db.commit()
        db.refresh(donante)
        return donante
    except IntegrityError as e:
        db.rollback()
        # Si es un error de clave duplicada, intentar resetear la secuencia y avisar al usuario
        if "duplicate key value violates unique constraint" in str(e.orig):
            db.execute(text("SELECT setval(pg_get_serial_sequence('donante', 'donante_id'), COALESCE(MAX(donante_id), 1)) FROM donante;"))
            db.commit()
            raise ValueError("Error: Secuencia de Donante desincronizada. Intente de nuevo.")
        raise ValueError(f"Error al crear donante: {e}")

def update_donante(db: Session, donante_id: int, data: dict):
    donante = get_donante(db, donante_id)
    if donante:
        for key, value in data.items():
            setattr(donante, key, value)
        db.commit()
        db.refresh(donante)
    return donante

def delete_donante(db: Session, donante_id: int):
    donante = get_donante(db, donante_id)
    if donante:
        db.delete(donante)
        db.commit()
        return True
    return False
