from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import (
    Cliente, ClienteCreate, 
    Producto, ProductoCreate,
    Venta, VentaCreate,
    Carta, CartaCreate
)
import crud

router = APIRouter()

# Clientes
@router.post("/", response_model=Cliente)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = crud.get_cliente_by_email(db, email=cliente.email)
    if db_cliente:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud.create_cliente(db=db, cliente=cliente)

@router.get("/", response_model=List[Cliente])
def leer_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_clientes(db, skip=skip, limit=limit)

@router.get("/{cliente_id}", response_model=Cliente)
def leer_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = crud.get_cliente(db, cliente_id=cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_cliente

# Productos
@router.post("/", response_model=Producto)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return crud.create_producto(db=db, producto=producto)

@router.get("/", response_model=List[Producto])
def leer_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_productos(db, skip=skip, limit=limit)

# Ventas
@router.post("/", response_model=Venta)
def crear_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    return crud.create_venta(db=db, venta=venta)

# Cartas
@router.post("/", response_model=Carta)
def crear_carta(carta: CartaCreate, db: Session = Depends(get_db)):
    return crud.create_carta(db=db, carta=carta)

@router.get("/por-rareza/{rareza_id}", response_model=List[Carta])
def leer_cartas_por_rareza(rareza_id: int, db: Session = Depends(get_db)):
    return crud.get_cartas_por_rareza(db, rareza_id=rareza_id)