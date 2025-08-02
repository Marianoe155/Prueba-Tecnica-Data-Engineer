-- ============================================
-- Datos de ejemplo para la base de datos
-- ============================================
-- 
-- Este archivo contiene datos de prueba para poblar
-- las tablas con información de ejemplo
--
-- ============================================

-- Conectarse a la base de datos y esquema
SET search_path TO app_schema, public;

-- ============================================
-- DATOS DE USUARIOS DE EJEMPLO
-- ============================================
INSERT INTO usuarios (nombre, email) VALUES
    ('María García', 'maria.garcia@email.com'),
    ('Carlos López', 'carlos.lopez@email.com'),
    ('Ana Martínez', 'ana.martinez@email.com'),
    ('Pedro Rodríguez', 'pedro.rodriguez@email.com'),
    ('Laura Fernández', 'laura.fernandez@email.com')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- DATOS DE PRODUCTOS DE EJEMPLO
-- ============================================
INSERT INTO productos (nombre, descripcion, precio, stock, categoria) VALUES
    ('Laptop Dell XPS 13', 'Laptop ultrabook con procesador Intel i7', 1299.99, 15, 'Electrónicos'),
    ('Mouse Inalámbrico Logitech', 'Mouse ergonómico con conexión Bluetooth', 29.99, 50, 'Accesorios'),
    ('Teclado Mecánico RGB', 'Teclado gaming con iluminación RGB', 89.99, 25, 'Accesorios'),
    ('Monitor 4K Samsung', 'Monitor de 27 pulgadas con resolución 4K', 399.99, 8, 'Electrónicos'),
    ('Auriculares Sony WH-1000XM4', 'Auriculares con cancelación de ruido', 249.99, 20, 'Audio'),
    ('Webcam HD Logitech', 'Cámara web Full HD para videoconferencias', 79.99, 30, 'Accesorios'),
    ('Tablet iPad Air', 'Tablet Apple con pantalla de 10.9 pulgadas', 599.99, 12, 'Electrónicos'),
    ('Cargador Portátil Anker', 'Power bank de 20000mAh con carga rápida', 45.99, 40, 'Accesorios'),
    ('Altavoz Bluetooth JBL', 'Altavoz portátil resistente al agua', 119.99, 18, 'Audio'),
    ('Disco Duro Externo 2TB', 'Almacenamiento externo USB 3.0', 89.99, 22, 'Almacenamiento')
ON CONFLICT DO NOTHING;

-- ============================================
-- DATOS DE CONFIGURACIONES ADICIONALES
-- ============================================
INSERT INTO configuraciones (clave, valor, descripcion) VALUES
    ('moneda_sistema', 'USD', 'Moneda utilizada en el sistema'),
    ('idioma_defecto', 'es', 'Idioma por defecto del sistema'),
    ('zona_horaria', 'America/Argentina/Buenos_Aires', 'Zona horaria del sistema'),
    ('email_notificaciones', 'admin@proyecto-data-engineer.com', 'Email para notificaciones del sistema'),
    ('limite_productos_carrito', '50', 'Número máximo de productos en el carrito'),
    ('descuento_mayorista', '10', 'Porcentaje de descuento para mayoristas'),
    ('stock_minimo_alerta', '5', 'Stock mínimo para generar alerta'),
    ('backup_automatico', 'true', 'Activar respaldos automáticos'),
    ('modo_debug', 'false', 'Activar modo de depuración')
ON CONFLICT (clave) DO NOTHING;

-- ============================================
-- DATOS DE PEDIDOS DE EJEMPLO
-- ============================================
INSERT INTO pedidos (usuario_id, total, estado, direccion_entrega, notas) VALUES
    (1, 1329.98, 'completado', 'Av. Corrientes 1234, CABA', 'Entrega en horario laboral'),
    (2, 119.98, 'pendiente', 'San Martín 567, Rosario', 'Llamar antes de entregar'),
    (3, 649.98, 'en_proceso', 'Belgrano 890, Córdoba', 'Portero 24hs'),
    (4, 89.99, 'completado', 'Mitre 321, Mendoza', 'Casa con portón azul'),
    (5, 369.97, 'pendiente', 'Rivadavia 456, La Plata', 'Departamento 4B')
ON CONFLICT DO NOTHING;

-- ============================================
-- DATOS DE DETALLE DE PEDIDOS
-- ============================================
INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario) VALUES
    -- Pedido 1
    (1, 1, 1, 1299.99),  -- Laptop Dell XPS 13
    (1, 2, 1, 29.99),    -- Mouse Inalámbrico
    
    -- Pedido 2
    (2, 3, 1, 89.99),    -- Teclado Mecánico
    (2, 2, 1, 29.99),    -- Mouse Inalámbrico
    
    -- Pedido 3
    (3, 7, 1, 599.99),   -- Tablet iPad Air
    (3, 8, 1, 45.99),    -- Cargador Portátil
    
    -- Pedido 4
    (4, 10, 1, 89.99),   -- Disco Duro Externo
    
    -- Pedido 5
    (5, 5, 1, 249.99),   -- Auriculares Sony
    (5, 9, 1, 119.99)    -- Altavoz Bluetooth
ON CONFLICT DO NOTHING;

-- ============================================
-- REGISTROS DE LOG DE EJEMPLO
-- ============================================
INSERT INTO logs_sistema (usuario_id, accion, descripcion, ip_address) VALUES
    (1, 'login', 'Usuario inició sesión correctamente', '192.168.1.100'),
    (1, 'crear_pedido', 'Pedido #1 creado exitosamente', '192.168.1.100'),
    (2, 'login', 'Usuario inició sesión correctamente', '192.168.1.101'),
    (2, 'ver_producto', 'Consultó detalles del producto: Teclado Mecánico RGB', '192.168.1.101'),
    (3, 'registro', 'Nuevo usuario registrado en el sistema', '192.168.1.102'),
    (1, 'actualizar_perfil', 'Usuario actualizó información de perfil', '192.168.1.100'),
    (4, 'login', 'Usuario inició sesión correctamente', '192.168.1.103'),
    (5, 'crear_pedido', 'Pedido #5 creado exitosamente', '192.168.1.104')
ON CONFLICT DO NOTHING;

-- Mensaje de confirmación
SELECT 'Datos de ejemplo insertados correctamente' AS resultado,
       (SELECT COUNT(*) FROM usuarios) AS total_usuarios,
       (SELECT COUNT(*) FROM productos) AS total_productos,
       (SELECT COUNT(*) FROM pedidos) AS total_pedidos;
