CREATE TYPE calidad_estado AS ENUM ('nuevo', 'usado', 'dañado');
CREATE TYPE metodo_pago AS ENUM ('efectivo', 'tarjeta', 'transferencia');
CREATE DOMAIN email_format AS TEXT CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Cliente
CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    email email_format UNIQUE NOT NULL,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    telefono VARCHAR(20)
);

-- Empleado
CREATE TABLE empleado (
    id_empleado SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    email email_format UNIQUE,
    cargo TEXT NOT NULL
);

-- Proveedor
CREATE TABLE proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    contacto TEXT,
    telefono VARCHAR(20)
);

-- Producto
CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio DECIMAL(10,2) CHECK (precio > 0),
    descripcion TEXT,
    calidad calidad_estado DEFAULT 'nuevo',
    stock_actual INTEGER DEFAULT 0 CHECK (stock_actual >= 0)
);

-- Relación producto-proveedor
CREATE TABLE producto_proveedor (
    id_producto INT REFERENCES producto(id_producto) ON DELETE CASCADE,
    id_proveedor INT REFERENCES proveedor(id_proveedor) ON DELETE CASCADE,
    fecha_compra DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (id_producto, id_proveedor)
);

-- Carta (herencia de producto)
CREATE TABLE carta (
    id_carta SERIAL PRIMARY KEY,
    id_producto INT REFERENCES producto(id_producto) ON DELETE CASCADE,
    codigo_carta VARCHAR(50) UNIQUE,
    id_categoria INT,
    id_rareza INT,
    id_tipo INT,
    idioma TEXT DEFAULT 'Inglés'
);

-- Rareza
CREATE TABLE rareza (
    id_rareza SERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL
);

-- Tipo de carta
CREATE TABLE tipo_carta (
    id_tipo SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL
);

-- Categoría de carta
CREATE TABLE categoria_carta (
    id_categoria SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL
);

-- Cliente - cartas favoritas
CREATE TABLE cliente_favoritas (
    id_cliente INT REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    id_carta INT REFERENCES carta(id_carta) ON DELETE CASCADE,
    PRIMARY KEY (id_cliente, id_carta)
);

-- Venta
CREATE TABLE venta (
    id_venta SERIAL PRIMARY KEY,
    id_cliente INT REFERENCES cliente(id_cliente),
    id_empleado INT REFERENCES empleado(id_empleado),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) DEFAULT 0
);

-- Venta-producto
CREATE TABLE venta_producto (
    id_venta INT REFERENCES venta(id_venta) ON DELETE CASCADE,
    id_producto INT REFERENCES producto(id_producto),
    cantidad INT CHECK (cantidad > 0),
    PRIMARY KEY (id_venta, id_producto)
);

-- Pago
CREATE TABLE pago (
    id_pago SERIAL PRIMARY KEY,
    id_venta INT REFERENCES venta(id_venta),
    monto DECIMAL(10,2),
    metodo metodo_pago,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock
CREATE TABLE stock (
    id_producto INT PRIMARY KEY REFERENCES producto(id_producto),
    cantidad INTEGER DEFAULT 0 CHECK (cantidad >= 0)
);

-- Tienda
CREATE TABLE tienda (
    id_tienda SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    direccion TEXT NOT NULL
);

-- Log de modificaciones
CREATE TABLE log_modificaciones (
    id_log SERIAL PRIMARY KEY,
    tabla TEXT NOT NULL,
    accion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario TEXT
);


-- Funciones
-- Calcular total de venta dado un ID
CREATE OR REPLACE FUNCTION calcular_total_venta(venta_id INT) RETURNS DECIMAL AS $$
    SELECT COALESCE(SUM(vp.cantidad * p.precio), 0)
    FROM venta_producto vp
    JOIN producto p ON vp.id_producto = p.id_producto
    WHERE vp.id_venta = venta_id;
$$ LANGUAGE SQL;

-- Obtener cartas favoritas por cliente
CREATE OR REPLACE FUNCTION cartas_favoritas_cliente(cliente_id INT)
RETURNS TABLE(id_carta INT, nombre TEXT) AS $$
    SELECT c.id_carta, p.nombre
    FROM cliente_favoritas cf
    JOIN carta c ON cf.id_carta = c.id_carta
    JOIN producto p ON c.id_producto = p.id_producto
    WHERE cf.id_cliente = cliente_id;
$$ LANGUAGE SQL;


-- Triggers
-- Trigger para actualizar automáticamente
CREATE OR REPLACE FUNCTION actualizar_total_venta() RETURNS TRIGGER AS $$
BEGIN
    UPDATE venta
    SET total = (
        SELECT COALESCE(SUM(vp.cantidad * p.precio), 0)
        FROM venta_producto vp
        JOIN producto p ON vp.id_producto = p.id_producto
        WHERE vp.id_venta = NEW.id_venta
    )
    WHERE id_venta = NEW.id_venta;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_actualizar_total
AFTER INSERT OR UPDATE OR DELETE ON venta_producto
FOR EACH ROW
EXECUTE FUNCTION actualizar_total_venta();


-- Trigger log de inserciones en producto
CREATE OR REPLACE FUNCTION log_insert_producto() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_modificaciones(tabla, accion, usuario)
    VALUES ('producto', 'INSERT', current_user);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_log_producto
AFTER INSERT ON producto
FOR EACH ROW EXECUTE FUNCTION log_insert_producto();

-- Trigger Validar que cartas solo se creen si existen en producto
CREATE OR REPLACE FUNCTION validar_producto_en_carta() RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM producto WHERE id_producto = NEW.id_producto) THEN
        RAISE EXCEPTION 'Producto no existe';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_validar_carta
BEFORE INSERT ON carta
FOR EACH ROW EXECUTE FUNCTION validar_producto_en_carta();

-- Trigger actualiza stock al vender
CREATE OR REPLACE FUNCTION actualizar_stock() RETURNS TRIGGER AS $$
BEGIN
    UPDATE producto
    SET stock_actual = stock_actual - NEW.cantidad
    WHERE id_producto = NEW.id_producto;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_stock_venta
AFTER INSERT ON venta_producto
FOR EACH ROW EXECUTE FUNCTION actualizar_stock();


-- Vistas
-- Resumen de ventas con cliente
CREATE VIEW vista_resumen_ventas AS
SELECT v.id_venta, c.nombre AS cliente, e.nombre AS empleado,
       v.fecha_venta, v.total
FROM venta v
JOIN cliente c ON v.id_cliente = c.id_cliente
JOIN empleado e ON v.id_empleado = e.id_empleado;

-- Inventario completo
CREATE VIEW vista_inventario AS
SELECT p.id_producto, p.nombre, p.precio, p.stock_actual, p.calidad
FROM producto p
ORDER BY p.stock_actual DESC;

-- Cartas por rareza
CREATE VIEW vista_cartas_por_rareza AS
SELECT r.descripcion AS rareza, COUNT(*) AS cantidad_cartas
FROM carta c
JOIN rareza r ON c.id_rareza = r.id_rareza
GROUP BY r.descripcion;


