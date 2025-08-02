-- ============================================
-- Scripts para crear tablas adicionales
-- ============================================
-- 
-- Este archivo contiene ejemplos de tablas adicionales
-- que puedes crear según las necesidades de tu proyecto
--
-- ============================================

-- Conectarse a la base de datos y esquema
-- \c proyecto_data_engineer;
SET search_path TO app_schema, public;

-- ============================================
-- TABLA DE PRODUCTOS (Ejemplo)
-- ============================================
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock INTEGER DEFAULT 0,
    categoria VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE productos IS 'Catálogo de productos del sistema';

-- ============================================
-- TABLA DE PEDIDOS (Ejemplo)
-- ============================================
CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega DATE,
    direccion_entrega TEXT,
    notas TEXT
);

COMMENT ON TABLE pedidos IS 'Pedidos realizados por los usuarios';

-- ============================================
-- TABLA DE DETALLE DE PEDIDOS (Ejemplo)
-- ============================================
CREATE TABLE IF NOT EXISTS detalle_pedidos (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

COMMENT ON TABLE detalle_pedidos IS 'Detalle de productos en cada pedido';

-- ============================================
-- ÍNDICES ADICIONALES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo);
CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON pedidos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
CREATE INDEX IF NOT EXISTS idx_detalle_pedido ON detalle_pedidos(pedido_id);

-- ============================================
-- FUNCIÓN PARA ACTUALIZAR TIMESTAMP
-- ============================================
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar automáticamente fecha_actualizacion
CREATE TRIGGER trigger_actualizar_productos
    BEFORE UPDATE ON productos
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

-- Otorgar permisos
GRANT SELECT, INSERT, UPDATE, DELETE ON productos, pedidos, detalle_pedidos TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app_schema TO app_user;
