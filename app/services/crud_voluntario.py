from sqlalchemy.orm import Session
from models import Voluntario

def get_voluntarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Voluntario).offset(skip).limit(limit).all()

def get_voluntario(db: Session, voluntario_id: int):
    return db.query(Voluntario).filter(Voluntario.voluntario_id == voluntario_id).first()

def create_voluntario(db: Session, data: dict):
    voluntario = Voluntario(
        nombre=data.get("nombre"),
        apellido=data.get("apellido"),
        email=data.get("email"),
        fecha_nacimiento=data.get("fecha_nacimiento"),
    )
    db.add(voluntario)
    db.commit()
    db.refresh(voluntario)
    return voluntario

def update_voluntario(db: Session, voluntario_id: int, data: dict):
    voluntario = db.query(Voluntario).filter(Voluntario.voluntario_id == voluntario_id).first()
    if not voluntario:
        return None
    for key, value in data.items():
        setattr(voluntario, key, value)
    db.commit()
    db.refresh(voluntario)
    return voluntario

def delete_voluntario(db: Session, voluntario_id: int):
    voluntario = db.query(Voluntario).filter(Voluntario.voluntario_id == voluntario_id).first()
    if not voluntario:
        return False
    db.delete(voluntario)
    db.commit()
    return True