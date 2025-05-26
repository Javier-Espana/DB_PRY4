from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

class CalidadEstado(str, PyEnum):
    NUEVO = 'nuevo'
    USADO = 'usado'
    DAÑADO = 'dañado'

class MetodoPago(str, PyEnum):
    EFECTIVO = 'efectivo'
    TARJETA = 'tarjeta'
    TRANSFERENCIA = 'transferencia'

class Cliente(Base):
    __tablename__ = 'cliente'
    
    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    fecha_registro = Column(Date, server_default='CURRENT_DATE')
    telefono = Column(String(20))
    
    ventas = relationship("Venta", back_populates="cliente")
    cartas_favoritas = relationship("Carta", secondary="cliente_favoritas", back_populates="clientes_favoritos")

class Empleado(Base):
    __tablename__ = 'empleado'
    
    id_empleado = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True)
    cargo = Column(String, nullable=False)
    
    ventas = relationship("Venta", back_populates="empleado")

class Proveedor(Base):
    __tablename__ = 'proveedor'
    
    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    contacto = Column(String)
    telefono = Column(String(20))
    
    productos = relationship("Producto", secondary="producto_proveedor", back_populates="proveedores")

class Producto(Base):
    __tablename__ = 'producto'
    
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, CheckConstraint('precio > 0'), nullable=False)
    descripcion = Column(String)
    calidad = Column(Enum(CalidadEstado), server_default='nuevo')
    stock_actual = Column(Integer, server_default='0', CheckConstraint('stock_actual >= 0'))
    
    proveedores = relationship("Proveedor", secondary="producto_proveedor", back_populates="productos")
    ventas = relationship("Venta", secondary="venta_producto", back_populates="productos")
    carta = relationship("Carta", uselist=False, back_populates="producto")

class ProductoProveedor(Base):
    __tablename__ = 'producto_proveedor'
    
    id_producto = Column(Integer, ForeignKey('producto.id_producto', ondelete='CASCADE'), primary_key=True)
    id_proveedor = Column(Integer, ForeignKey('proveedor.id_proveedor', ondelete='CASCADE'), primary_key=True)
    fecha_compra = Column(Date, server_default='CURRENT_DATE')

class Carta(Base):
    __tablename__ = 'carta'
    
    id_carta = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey('producto.id_producto', ondelete='CASCADE'))
    codigo_carta = Column(String(50), unique=True)
    id_categoria = Column(Integer, ForeignKey('categoria_carta.id_categoria'))
    id_rareza = Column(Integer, ForeignKey('rareza.id_rareza'))
    id_tipo = Column(Integer, ForeignKey('tipo_carta.id_tipo'))
    idioma = Column(String, server_default='Inglés')
    
    producto = relationship("Producto", back_populates="carta")
    categoria = relationship("CategoriaCarta")
    rareza = relationship("Rareza")
    tipo = relationship("TipoCarta")
    clientes_favoritos = relationship("Cliente", secondary="cliente_favoritas", back_populates="cartas_favoritas")

class Rareza(Base):
    __tablename__ = 'rareza'
    
    id_rareza = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, nullable=False)

class TipoCarta(Base):
    __tablename__ = 'tipo_carta'
    
    id_tipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

class CategoriaCarta(Base):
    __tablename__ = 'categoria_carta'
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

class ClienteFavoritas(Base):
    __tablename__ = 'cliente_favoritas'
    
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente', ondelete='CASCADE'), primary_key=True)
    id_carta = Column(Integer, ForeignKey('carta.id_carta', ondelete='CASCADE'), primary_key=True)

class Venta(Base):
    __tablename__ = 'venta'
    
    id_venta = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'))
    id_empleado = Column(Integer, ForeignKey('empleado.id_empleado'))
    fecha_venta = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    total = Column(Float, server_default='0')
    
    cliente = relationship("Cliente", back_populates="ventas")
    empleado = relationship("Empleado", back_populates="ventas")
    productos = relationship("Producto", secondary="venta_producto", back_populates="ventas")
    pagos = relationship("Pago", back_populates="venta")

class VentaProducto(Base):
    __tablename__ = 'venta_producto'
    
    id_venta = Column(Integer, ForeignKey('venta.id_venta', ondelete='CASCADE'), primary_key=True)
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), primary_key=True)
    cantidad = Column(Integer, CheckConstraint('cantidad > 0'))

class Pago(Base):
    __tablename__ = 'pago'
    
    id_pago = Column(Integer, primary_key=True, index=True)
    id_venta = Column(Integer, ForeignKey('venta.id_venta'))
    monto = Column(Float)
    metodo = Column(Enum(MetodoPago))
    fecha_pago = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    
    venta = relationship("Venta", back_populates="pagos")

class Stock(Base):
    __tablename__ = 'stock'
    
    id_producto = Column(Integer, ForeignKey('producto.id_producto'), primary_key=True)
    cantidad = Column(Integer, server_default='0', CheckConstraint('cantidad >= 0'))

class Tienda(Base):
    __tablename__ = 'tienda'
    
    id_tienda = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)

class LogModificaciones(Base):
    __tablename__ = 'log_modificaciones'
    
    id_log = Column(Integer, primary_key=True, index=True)
    tabla = Column(String, nullable=False)
    accion = Column(String)
    fecha = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    usuario = Column(String)