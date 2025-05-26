from sqlalchemy.orm import Session
from models import Carta
from schemas import CartaCreate

def get_carta(db: Session, carta_id: int):
    return db.query(Carta).filter(Carta.id_carta == carta_id).first()

def get_cartas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Carta).offset(skip).limit(limit).all()

def create_carta(db: Session, carta: CartaCreate):
    db_carta = Carta(**carta.dict())
    db.add(db_carta)
    db.commit()
    db.refresh(db_carta)
    return db_carta

def get_cartas_por_rareza(db: Session, rareza_id: int):
    return db.query(Carta).filter(Carta.id_rareza == rareza_id).all()