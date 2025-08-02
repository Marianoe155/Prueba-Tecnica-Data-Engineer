-- ============================================
-- Configuración inicial de tablas
-- ============================================
-- 
-- INSTRUCCIONES DE USO:
-- 1. Asegúrate de haber creado la base de datos con create_database.sql
-- 2. Conéctate a la base de datos 'proyecto_data_engineer'
-- 3. Ejecuta este script completo
--
-- ============================================

-- Conectarse a la base de datos (comentario informativo)
-- \c proyecto_data_engineer;

-- Crear esquema para organizar las tablas
CREATE SCHEMA IF NOT EXISTS app_schema;

-- Establecer el esquema por defecto
SET search_path TO app_schema, public;

-- ============================================
-- TABLA DE USUARIOS
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Comentario descriptivo
COMMENT ON TABLE usuarios IS 'Tabla principal de usuarios del sistema';
COMMENT ON COLUMN usuarios.id IS 'Identificador único del usuario';
COMMENT ON COLUMN usuarios.nombre IS 'Nombre completo del usuario';
COMMENT ON COLUMN usuarios.email IS 'Correo electrónico único del usuario';

-- ============================================
-- TABLA DE CONFIGURACIONES
-- ============================================
CREATE TABLE IF NOT EXISTS configuraciones (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(50) UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comentario descriptivo
COMMENT ON TABLE configuraciones IS 'Configuraciones generales del sistema';

-- ============================================
-- TABLA DE LOGS/REGISTROS
-- ============================================
CREATE TABLE IF NOT EXISTS logs_sistema (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET
);

-- Comentario descriptivo
COMMENT ON TABLE logs_sistema IS 'Registro de actividades del sistema';

-- ============================================
-- ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_logs_fecha ON logs_sistema(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_logs_usuario ON logs_sistema(usuario_id);

-- ============================================
-- DATOS INICIALES DE EJEMPLO
-- ============================================

-- Insertar configuraciones básicas
INSERT INTO configuraciones (clave, valor, descripcion) VALUES
    ('version_sistema', '1.0.0', 'Versión actual del sistema'),
    ('mantenimiento', 'false', 'Indica si el sistema está en mantenimiento'),
    ('max_usuarios', '1000', 'Número máximo de usuarios permitidos')
ON CONFLICT (clave) DO NOTHING;

-- Insertar usuario administrador de ejemplo
INSERT INTO usuarios (nombre, email) VALUES
    ('Administrador', 'admin@proyecto-data-engineer.com')
ON CONFLICT (email) DO NOTHING;

-- Otorgar permisos al usuario de la aplicación
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_schema TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app_schema TO app_user;

-- Mensaje de confirmación
SELECT 'Configuración inicial completada exitosamente' AS resultado;
