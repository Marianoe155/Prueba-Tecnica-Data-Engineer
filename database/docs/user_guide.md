# 👥 Guía del Usuario - Base de Datos PostgreSQL

## 🎯 Para Usuarios No Técnicos

Esta guía te explica cómo usar la base de datos de forma sencilla, sin necesidad de conocimientos técnicos avanzados.

## 🖥️ Herramientas Disponibles

### pgAdmin (Recomendado para principiantes)
- **¿Qué es?**: Una interfaz gráfica fácil de usar
- **¿Cómo acceder?**: Busca "pgAdmin" en el menú de inicio
- **Ventajas**: No necesitas escribir comandos, todo es visual

### psql (Para usuarios avanzados)
- **¿Qué es?**: Línea de comandos
- **¿Cómo acceder?**: Abre "Command Prompt" y escribe `psql`

## 🔐 Información de Conexión

Para conectarte a la base de datos, usa estos datos:

```
Servidor/Host: localhost
Puerto: 5432
Base de datos: proyecto_data_engineer
Usuario: postgres (o app_user)
Contraseña: [la que configuraste durante la instalación]
```

## 📝 Tareas Comunes

### ✅ Conectarse a la Base de Datos

**Con pgAdmin:**
1. Abre pgAdmin
2. Haz clic en "Add New Server"
3. Ingresa los datos de conexión
4. Haz clic en "Save"

**Con psql:**
```bash
psql -h localhost -p 5432 -U postgres -d proyecto_data_engineer
```

### 👀 Ver los Datos

**Con pgAdmin:**
1. Navega a: Servers → tu_servidor → Databases → proyecto_data_engineer → Schemas → app_schema → Tables
2. Haz clic derecho en una tabla → "View/Edit Data" → "All Rows"

**Con psql:**
```sql
-- Ver todos los usuarios
SELECT * FROM app_schema.usuarios;

-- Ver configuraciones
SELECT * FROM app_schema.configuraciones;
```

### ➕ Agregar Nuevos Datos

**Ejemplo - Agregar un nuevo usuario:**
```sql
INSERT INTO app_schema.usuarios (nombre, email) 
VALUES ('Juan Pérez', 'juan@email.com');
```

### 🔍 Buscar Información

**Ejemplo - Buscar un usuario por email:**
```sql
SELECT * FROM app_schema.usuarios 
WHERE email = 'juan@email.com';
```

## 🛡️ Respaldos (Backups)

### Crear un Respaldo
```bash
pg_dump -h localhost -U postgres proyecto_data_engineer > backup_fecha.sql
```

### Restaurar un Respaldo
```bash
psql -h localhost -U postgres proyecto_data_engineer < backup_fecha.sql
```

## ⚠️ Consejos Importantes

1. **Siempre haz respaldos** antes de hacer cambios importantes
2. **No elimines datos** sin estar seguro
3. **Usa el usuario 'app_user'** para operaciones diarias
4. **Guarda el usuario 'postgres'** solo para administración

## 🆘 Solución de Problemas

### No puedo conectarme
- Verifica que PostgreSQL esté ejecutándose
- Confirma que la contraseña sea correcta
- Asegúrate de usar el puerto correcto (5432)

### Error de permisos
- Usa el usuario correcto (postgres o app_user)
- Verifica que el usuario tenga permisos en la tabla

### La base de datos no existe
- Ejecuta primero el script `create_database.sql`
- Luego ejecuta `initial_setup.sql`

## 📞 Contacto

Si necesitas ayuda adicional, contacta al equipo técnico con:
- Descripción del problema
- Mensaje de error (si aparece)
- Pasos que seguiste antes del problema
