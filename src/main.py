from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Base
import crud.cliente as crud_cliente
import crud.producto as crud_producto
from schemas import ClienteCreate, Cliente, ProductoCreate, Producto

app = FastAPI()

@app.on_event("startup")
def startup_event():
    # Crear tablas si no existen (en producción usar migraciones)
    Base.metadata.create_all(bind=get_db().__next__().bind)

@app.post("/clientes/", response_model=Cliente)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = crud_cliente.get_cliente_by_email(db, email=cliente.email)
    if db_cliente:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud_cliente.create_cliente(db=db, cliente=cliente)

@app.get("/clientes/", response_model=list[Cliente])
def read_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clientes = crud_cliente.get_clientes(db, skip=skip, limit=limit)
    return clientes

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def read_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = crud_cliente.get_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def update_cliente(cliente_id: int, cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = crud_cliente.get_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return crud_cliente.update_cliente(db=db, cliente_id=cliente_id, cliente=cliente)

@app.delete("/clientes/{cliente_id}", response_model=Cliente)
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = crud_cliente.get_cliente(db, cliente_id=cliente_id)
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return crud_cliente.delete_cliente(db=db, cliente_id=cliente_id)

# Rutas similares para Producto, Venta, etc.