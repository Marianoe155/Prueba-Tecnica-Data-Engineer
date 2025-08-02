# 📥 Guía de Instalación de PostgreSQL

Esta guía te ayudará a instalar PostgreSQL en tu computadora de forma sencilla.

## 🖥️ Para Windows

### Paso 1: Descargar PostgreSQL
1. Ve a la página oficial: https://www.postgresql.org/download/windows/
2. Haz clic en "Download the installer"
3. Descarga la versión más reciente (recomendada: PostgreSQL 15 o superior)

### Paso 2: Instalar PostgreSQL
1. Ejecuta el archivo descargado como administrador
2. Sigue el asistente de instalación:
   - **Puerto**: Deja el puerto por defecto (5432)
   - **Contraseña**: Crea una contraseña segura para el usuario 'postgres' (¡ANÓTALA!)
   - **Locale**: Selecciona tu idioma/región
3. Instala también pgAdmin (interfaz gráfica) cuando se te pregunte

### Paso 3: Verificar la instalación
1. Abre el "Command Prompt" (cmd)
2. Escribe: `psql --version`
3. Si ves la versión de PostgreSQL, ¡la instalación fue exitosa!

## 🔑 Información Importante

- **Usuario por defecto**: `postgres`
- **Puerto por defecto**: `5432`
- **Host**: `localhost`
- **Contraseña**: La que configuraste durante la instalación

## 🛠️ Herramientas Instaladas

- **psql**: Cliente de línea de comandos
- **pgAdmin**: Interfaz gráfica para administrar bases de datos
- **PostgreSQL Server**: El servidor de base de datos

## ❓ Problemas Comunes

### "psql no se reconoce como comando"
- Reinicia tu computadora después de la instalación
- O agrega PostgreSQL al PATH del sistema

### No puedo conectarme
- Verifica que el servicio PostgreSQL esté ejecutándose
- Ve a Servicios de Windows y busca "postgresql"

## ✅ Siguiente Paso
Una vez instalado PostgreSQL, continúa con `create_database.sql` para crear tu base de datos.
