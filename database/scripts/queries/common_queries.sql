-- ============================================
-- Consultas Frecuentes y Útiles
-- ============================================
-- 
-- Este archivo contiene consultas SQL comunes
-- que puedes usar como referencia o ejecutar directamente
--
-- ============================================

-- Conectarse al esquema correcto
SET search_path TO app_schema, public;

-- ============================================
-- CONSULTAS DE USUARIOS
-- ============================================

-- Ver todos los usuarios activos
SELECT id, nombre, email, fecha_creacion 
FROM usuarios 
WHERE activo = true 
ORDER BY fecha_creacion DESC;

-- Buscar usuario por email
SELECT * FROM usuarios 
WHERE email ILIKE '%garcia%';

-- Contar usuarios por estado
SELECT 
    activo,
    COUNT(*) as cantidad_usuarios
FROM usuarios 
GROUP BY activo;

-- ============================================
-- CONSULTAS DE PRODUCTOS
-- ============================================

-- Ver productos con stock bajo
SELECT nombre, stock, categoria 
FROM productos 
WHERE stock < 10 AND activo = true
ORDER BY stock ASC;

-- Productos más caros por categoría
SELECT 
    categoria,
    nombre,
    precio
FROM productos p1
WHERE precio = (
    SELECT MAX(precio) 
    FROM productos p2 
    WHERE p2.categoria = p1.categoria
)
ORDER BY categoria;

-- Valor total del inventario por categoría
SELECT 
    categoria,
    COUNT(*) as cantidad_productos,
    SUM(stock) as stock_total,
    SUM(precio * stock) as valor_inventario
FROM productos 
WHERE activo = true
GROUP BY categoria
ORDER BY valor_inventario DESC;

-- ============================================
-- CONSULTAS DE PEDIDOS
-- ============================================

-- Pedidos pendientes con información del usuario
SELECT 
    p.id as pedido_id,
    u.nombre as cliente,
    u.email,
    p.total,
    p.fecha_pedido,
    p.estado
FROM pedidos p
JOIN usuarios u ON p.usuario_id = u.id
WHERE p.estado = 'pendiente'
ORDER BY p.fecha_pedido DESC;

-- Resumen de ventas por mes
SELECT 
    DATE_TRUNC('month', fecha_pedido) as mes,
    COUNT(*) as cantidad_pedidos,
    SUM(total) as ventas_totales,
    AVG(total) as ticket_promedio
FROM pedidos 
WHERE estado = 'completado'
GROUP BY DATE_TRUNC('month', fecha_pedido)
ORDER BY mes DESC;

-- Top 5 clientes por volumen de compras
SELECT 
    u.nombre,
    u.email,
    COUNT(p.id) as cantidad_pedidos,
    SUM(p.total) as total_comprado
FROM usuarios u
JOIN pedidos p ON u.id = p.usuario_id
WHERE p.estado = 'completado'
GROUP BY u.id, u.nombre, u.email
ORDER BY total_comprado DESC
LIMIT 5;

-- ============================================
-- CONSULTAS DE DETALLE DE PEDIDOS
-- ============================================

-- Productos más vendidos
SELECT 
    pr.nombre,
    pr.categoria,
    SUM(dp.cantidad) as unidades_vendidas,
    SUM(dp.subtotal) as ingresos_totales
FROM detalle_pedidos dp
JOIN productos pr ON dp.producto_id = pr.id
JOIN pedidos p ON dp.pedido_id = p.id
WHERE p.estado = 'completado'
GROUP BY pr.id, pr.nombre, pr.categoria
ORDER BY unidades_vendidas DESC
LIMIT 10;

-- Detalle completo de un pedido específico
SELECT 
    p.id as pedido_id,
    u.nombre as cliente,
    pr.nombre as producto,
    dp.cantidad,
    dp.precio_unitario,
    dp.subtotal,
    p.total as total_pedido,
    p.estado
FROM pedidos p
JOIN usuarios u ON p.usuario_id = u.id
JOIN detalle_pedidos dp ON p.id = dp.pedido_id
JOIN productos pr ON dp.producto_id = pr.id
WHERE p.id = 1  -- Cambiar por el ID del pedido que quieras consultar
ORDER BY dp.id;

-- ============================================
-- CONSULTAS DE LOGS Y AUDITORÍA
-- ============================================

-- Actividad reciente del sistema
SELECT 
    l.fecha_hora,
    u.nombre as usuario,
    l.accion,
    l.descripcion,
    l.ip_address
FROM logs_sistema l
LEFT JOIN usuarios u ON l.usuario_id = u.id
ORDER BY l.fecha_hora DESC
LIMIT 20;

-- Usuarios más activos
SELECT 
    u.nombre,
    COUNT(l.id) as cantidad_acciones,
    MAX(l.fecha_hora) as ultima_actividad
FROM usuarios u
JOIN logs_sistema l ON u.id = l.usuario_id
GROUP BY u.id, u.nombre
ORDER BY cantidad_acciones DESC;

-- ============================================
-- CONSULTAS DE CONFIGURACIÓN
-- ============================================

-- Ver todas las configuraciones del sistema
SELECT 
    clave,
    valor,
    descripcion,
    fecha_actualizacion
FROM configuraciones
ORDER BY clave;

-- Buscar configuración específica
SELECT * FROM configuraciones 
WHERE clave = 'version_sistema';

-- ============================================
-- CONSULTAS DE ESTADÍSTICAS GENERALES
-- ============================================

-- Dashboard general del sistema
SELECT 
    'Usuarios Totales' as metrica,
    COUNT(*)::text as valor
FROM usuarios
WHERE activo = true

UNION ALL

SELECT 
    'Productos Activos' as metrica,
    COUNT(*)::text as valor
FROM productos
WHERE activo = true

UNION ALL

SELECT 
    'Pedidos Este Mes' as metrica,
    COUNT(*)::text as valor
FROM pedidos
WHERE DATE_TRUNC('month', fecha_pedido) = DATE_TRUNC('month', CURRENT_DATE)

UNION ALL

SELECT 
    'Ventas Este Mes' as metrica,
    CONCAT('$', ROUND(SUM(total), 2)::text) as valor
FROM pedidos
WHERE DATE_TRUNC('month', fecha_pedido) = DATE_TRUNC('month', CURRENT_DATE)
AND estado = 'completado';

-- ============================================
-- CONSULTAS DE MANTENIMIENTO
-- ============================================

-- Verificar integridad de datos
SELECT 
    'Pedidos sin usuario' as problema,
    COUNT(*) as cantidad
FROM pedidos p
LEFT JOIN usuarios u ON p.usuario_id = u.id
WHERE u.id IS NULL

UNION ALL

SELECT 
    'Detalles sin pedido' as problema,
    COUNT(*) as cantidad
FROM detalle_pedidos dp
LEFT JOIN pedidos p ON dp.pedido_id = p.id
WHERE p.id IS NULL

UNION ALL

SELECT 
    'Detalles sin producto' as problema,
    COUNT(*) as cantidad
FROM detalle_pedidos dp
LEFT JOIN productos pr ON dp.producto_id = pr.id
WHERE pr.id IS NULL;
