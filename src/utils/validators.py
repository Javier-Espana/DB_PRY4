from sqlalchemy.orm import Session
from database import SessionLocal

def validar_email_unico(email: str, exclude_id: int = None):
    db = SessionLocal()
    try:
        query = db.query(Cliente).filter(Cliente.email == email)
        if exclude_id:
            query = query.filter(Cliente.id_cliente != exclude_id)
        return query.first() is None
    finally:
        db.close()

def validar_stock_suficiente(producto_id: int, cantidad: int):
    db = SessionLocal()
    try:
        producto = db.query(Producto).get(producto_id)
        return producto and producto.stock_actual >= cantidad
    finally:
        db.close()