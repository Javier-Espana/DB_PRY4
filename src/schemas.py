from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum

class CalidadEstado(str, Enum):
    nuevo = "nuevo"
    usado = "usado"
    dañado = "dañado"

class MetodoPago(str, Enum):
    efectivo = "efectivo"
    tarjeta = "tarjeta"
    transferencia = "transferencia"

class ClienteBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id_cliente: int
    fecha_registro: date

    class Config:
        orm_mode = True

class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    precio: float = Field(..., gt=0)
    descripcion: Optional[str] = None
    calidad: Optional[CalidadEstado] = CalidadEstado.nuevo
    stock_actual: Optional[int] = Field(0, ge=0)

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id_producto: int

    class Config:
        orm_mode = True

class CartaBase(BaseModel):
    codigo_carta: str = Field(..., max_length=50)
    id_categoria: int
    id_rareza: int
    id_tipo: int
    idioma: Optional[str] = "Inglés"

class CartaCreate(CartaBase):
    id_producto: int

class Carta(CartaBase):
    id_carta: int
    producto: Producto

    class Config:
        orm_mode = True

class VentaBase(BaseModel):
    id_cliente: int
    id_empleado: int
    total: Optional[float] = 0

class VentaCreate(VentaBase):
    productos: list[dict] = Field(..., example=[{"id_producto": 1, "cantidad": 2}])

class Venta(VentaBase):
    id_venta: int
    fecha_venta: datetime
    cliente: Cliente

    class Config:
        orm_mode = True

class PagoBase(BaseModel):
    id_venta: int
    monto: float
    metodo: MetodoPago

class PagoCreate(PagoBase):
    pass

class Pago(PagoBase):
    id_pago: int
    fecha_pago: datetime

    class Config:
        orm_mode = True