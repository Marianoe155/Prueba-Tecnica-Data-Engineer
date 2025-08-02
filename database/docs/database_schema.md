# 📊 Esquema de la Base de Datos

## Información General

- **Nombre de la Base de Datos**: `proyecto_data_engineer`
- **Esquema Principal**: `app_schema`
- **Usuario de Aplicación**: `app_user`
- **Puerto**: `5432` (por defecto)

## 📋 Tablas del Sistema

### 1. Tabla `usuarios`
Almacena la información de los usuarios del sistema.

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | SERIAL | Identificador único | PRIMARY KEY |
| `nombre` | VARCHAR(100) | Nombre completo | NOT NULL |
| `email` | VARCHAR(150) | Correo electrónico | UNIQUE, NOT NULL |
| `fecha_creacion` | TIMESTAMP | Fecha de registro | DEFAULT CURRENT_TIMESTAMP |
| `activo` | BOOLEAN | Estado del usuario | DEFAULT TRUE |

### 2. Tabla `configuraciones`
Guarda las configuraciones generales del sistema.

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | SERIAL | Identificador único | PRIMARY KEY |
| `clave` | VARCHAR(50) | Nombre de la configuración | UNIQUE, NOT NULL |
| `valor` | TEXT | Valor de la configuración | - |
| `descripcion` | TEXT | Descripción de la configuración | - |
| `fecha_actualizacion` | TIMESTAMP | Última actualización | DEFAULT CURRENT_TIMESTAMP |

### 3. Tabla `logs_sistema`
Registra las actividades y eventos del sistema.

| Campo | Tipo | Descripción | Restricciones |
|-------|------|-------------|---------------|
| `id` | SERIAL | Identificador único | PRIMARY KEY |
| `usuario_id` | INTEGER | ID del usuario | FOREIGN KEY → usuarios(id) |
| `accion` | VARCHAR(100) | Tipo de acción realizada | NOT NULL |
| `descripcion` | TEXT | Descripción detallada | - |
| `fecha_hora` | TIMESTAMP | Momento del evento | DEFAULT CURRENT_TIMESTAMP |
| `ip_address` | INET | Dirección IP del usuario | - |

## 🔗 Relaciones

```
usuarios (1) ←→ (N) logs_sistema
```

- Un usuario puede tener múltiples registros en los logs
- Los logs están vinculados a usuarios específicos

## 📈 Índices

Para mejorar el rendimiento de las consultas:

- `idx_usuarios_email`: Índice en el campo email de usuarios
- `idx_logs_fecha`: Índice en fecha_hora de logs_sistema
- `idx_logs_usuario`: Índice en usuario_id de logs_sistema

## 🔧 Configuraciones Iniciales

El sistema incluye estas configuraciones por defecto:

| Clave | Valor | Descripción |
|-------|-------|-------------|
| `version_sistema` | 1.0.0 | Versión actual del sistema |
| `mantenimiento` | false | Estado de mantenimiento |
| `max_usuarios` | 1000 | Límite de usuarios |

## 👤 Usuario Administrador

Se crea automáticamente un usuario administrador:
- **Email**: admin@proyecto-data-engineer.com
- **Nombre**: Administrador
