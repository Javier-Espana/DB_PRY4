from sqlalchemy.orm import Session
from models import Venta, VentaProducto
from schemas import VentaCreate
from .producto import get_producto

def get_venta(db: Session, venta_id: int):
    return db.query(Venta).filter(Venta.id_venta == venta_id).first()

def get_ventas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Venta).offset(skip).limit(limit).all()

def create_venta(db: Session, venta: VentaCreate):
    db_venta = Venta(
        id_cliente=venta.id_cliente,
        id_empleado=venta.id_empleado
    )
    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)
    
    # Agregar productos a la venta
    for item in venta.productos:
        producto = get_producto(db, item["id_producto"])
        if producto:
            db_item = VentaProducto(
                id_venta=db_venta.id_venta,
                id_producto=producto.id_producto,
                cantidad=item["cantidad"]
            )
            db.add(db_item)
    
    db.commit()
    db.refresh(db_venta)
    return db_venta

def calcular_total_venta(db: Session, venta_id: int):
    venta = get_venta(db, venta_id)
    if not venta:
        return None
    
    total = sum(
        vp.cantidad * vp.producto.precio 
        for vp in venta.productos_assoc
    )
    
    venta.total = total
    db.commit()
    db.refresh(venta)
    return venta