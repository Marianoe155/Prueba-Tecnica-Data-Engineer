-- ============================================
-- Script para crear la base de datos principal
-- ============================================
-- 
-- INSTRUCCIONES DE USO:
-- 1. Abre pgAdmin o el terminal psql
-- 2. Conéctate como usuario 'postgres'
-- 3. Ejecuta este script completo
--
-- ============================================

-- Crear la base de datos principal
CREATE DATABASE proyecto_data_engineer
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Spain.1252'
    LC_CTYPE = 'Spanish_Spain.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Comentario descriptivo para la base de datos
COMMENT ON DATABASE proyecto_data_engineer 
    IS 'Base de datos principal para el proyecto Data Engineer - Contiene todas las tablas y datos del sistema';

-- Crear un usuario específico para la aplicación (opcional pero recomendado)
CREATE USER app_user WITH
    LOGIN
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    PASSWORD 'app_password_2024';

-- Otorgar permisos al usuario de la aplicación
GRANT CONNECT ON DATABASE proyecto_data_engineer TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT CREATE ON SCHEMA public TO app_user;

-- Mensaje de confirmación
-- (Este comentario aparecerá en los logs)
-- Base de datos 'proyecto_data_engineer' creada exitosamente
