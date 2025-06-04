from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from models import Voluntario

def get_voluntarios(db: Session):
    return db.query(Voluntario).all()

def get_voluntario(db: Session, voluntario_id: int):
    return db.query(Voluntario).filter(Voluntario.voluntario_id == voluntario_id).first()

def create_voluntario(db: Session, data: dict):
    try:
        data.pop('voluntario_id', None)
        # Normaliza enums a minúsculas y sin tildes si existen
        if "nivel_habilidad" in data and isinstance(data["nivel_habilidad"], str):
            data["nivel_habilidad"] = (
                data["nivel_habilidad"].lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            )
        voluntario = Voluntario(**data)
        db.add(voluntario)
        db.commit()
        db.refresh(voluntario)
        return voluntario
    except IntegrityError as e:
        db.rollback()
        # Si es un error de clave duplicada, resetear la secuencia y reintentar SOLO UNA VEZ
        if "duplicate key value violates unique constraint" in str(e.orig):
            db.execute(text("SELECT setval(pg_get_serial_sequence('voluntario', 'voluntario_id'), COALESCE(MAX(voluntario_id), 1)) FROM voluntario;"))
            db.commit()
            try:
                if "nivel_habilidad" in data and isinstance(data["nivel_habilidad"], str):
                    data["nivel_habilidad"] = (
                        data["nivel_habilidad"].lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    )
                voluntario = Voluntario(**data)
                db.add(voluntario)
                db.commit()
                db.refresh(voluntario)
                return voluntario
            except IntegrityError as e2:
                db.rollback()
                raise ValueError(f"Error persistente de secuencia de Voluntario: {e2}")
        raise ValueError(f"Error al crear voluntario: {e}")

def update_voluntario(db: Session, voluntario_id: int, data: dict):
    voluntario = get_voluntario(db, voluntario_id)
    if voluntario:
        if "nivel_habilidad" in data and isinstance(data["nivel_habilidad"], str):
            data["nivel_habilidad"] = (
                data["nivel_habilidad"].lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            )
        for key, value in data.items():
            setattr(voluntario, key, value)
        db.commit()
        db.refresh(voluntario)
    return voluntario

def delete_voluntario(db: Session, voluntario_id: int):
    voluntario = get_voluntario(db, voluntario_id)
    if voluntario:
        db.delete(voluntario)
        db.commit()
        return True
    return False