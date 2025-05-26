from sqlalchemy import event
from models import Producto, VentaProducto, LogModificaciones
from database import SessionLocal

def register_triggers():
    @event.listens_for(Producto, 'after_insert')
    def log_producto_insert(mapper, connection, target):
        db = SessionLocal()
        try:
            log = LogModificaciones(
                tabla="producto",
                accion="INSERT",
                usuario="system"
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

    @event.listens_for(VentaProducto, 'after_insert')
    def update_stock_after_sale(mapper, connection, target):
        db = SessionLocal()
        try:
            producto = db.query(Producto).get(target.id_producto)
            if producto:
                producto.stock_actual -= target.cantidad
                db.commit()
        finally:
            db.close()