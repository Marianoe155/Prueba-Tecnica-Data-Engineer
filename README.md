# 🚀 Guía Completa de Apache Airflow con Docker

**Configuración completa de Apache Airflow usando microservicios Docker. ¡Levántalo en minutos!**

## 📋 Prerrequisitos

- ✅ **Docker Desktop** instalado y funcionando
- ✅ **PowerShell** (en Windows)
- ✅ **Terminal** abierto en este directorio

## 🏗️ Estructura del Proyecto

```
📁 Prueba-Tecnica-Data-Engineer/
├── 📄 docker-compose.yml    # Configuración de servicios Docker
├── 📄 Dockerfile           # Imagen personalizada de Airflow (opcional)
├── 📄 .env                # Variables de entorno
├── 📄 init-airflow.sh     # Script de inicialización
├── 📁 dags/               # Directorio para DAGs de Airflow
│   └── 📄 example_dag.py  # DAG de ejemplo
└── 📄 README.md           # Esta guía
```

## 🚀 INICIO RÁPIDO - 4 Pasos Simples

### Paso 1: Levantar los Servicios

En PowerShell, ejecuta:

```powershell
docker-compose up -d
```

**¿Qué hace esto?** Levanta todos los contenedores (PostgreSQL, Redis, Airflow Webserver, Scheduler) en segundo plano.

### Paso 2: Inicializar la Base de Datos (Solo la primera vez)

```powershell
docker-compose run --rm webserver airflow db init
```

**¿Qué hace esto?** Crea las tablas necesarias en la base de datos PostgreSQL.

### Paso 3: Crear Usuario Administrador (Solo la primera vez)

```powershell
docker-compose run --rm webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

**¿Qué hace esto?** Crea un usuario admin para acceder a la interfaz web.

### Paso 4: Acceder a Airflow

🌐 **Abre tu navegador y visita:** [http://localhost:8080](http://localhost:8080)

**Credenciales de acceso:**
- 👤 **Usuario:** `admin`
- 🔑 **Contraseña:** `admin`

---

## 🔧 Comandos Útiles

### Ver el estado de los servicios
```powershell
docker-compose ps
```

### Ver logs en tiempo real
```powershell
docker-compose logs -f
```

### Ver logs de un servicio específico
```powershell
docker-compose logs -f webserver
docker-compose logs -f scheduler
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Reiniciar servicios
```powershell
docker-compose restart
```

### Parar todos los servicios
```powershell
docker-compose down
```

### Parar y eliminar datos (⚠️ CUIDADO: Borra la base de datos)
```powershell
docker-compose down -v
```

### Ejecutar comandos dentro de Airflow
```powershell
docker-compose run --rm webserver airflow <comando>
```

---

## 📊 Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|---------|-------------|
| 🌐 **Webserver** | 8080 | Interfaz web de Airflow |
| 📅 **Scheduler** | - | Programador de tareas |
| 🗄️ **PostgreSQL** | 5432 | Base de datos para metadatos |
| 🔄 **Redis** | 6379 | Message broker para Celery |

---

## 📝 Trabajando con DAGs

### Agregar un nuevo DAG

1. **Crea tu archivo DAG** en la carpeta `dags/`
2. **El DAG aparecerá automáticamente** en la interfaz web
3. **No necesitas reiniciar** los servicios

### Ejemplo de DAG básico

```python
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime

default_args = {
    'owner': 'tu_nombre',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

dag = DAG(
    'mi_primer_dag',
    default_args=default_args,
    description='Mi primer DAG',
    schedule_interval='@daily',
)

task1 = DummyOperator(task_id='tarea_1', dag=dag)
task2 = DummyOperator(task_id='tarea_2', dag=dag)

task1 >> task2
```

---

## 🛠️ Solución de Problemas

### Problema: "Cannot connect to Docker daemon"
**Solución:** Asegúrate de que Docker Desktop esté ejecutándose.

### Problema: Puerto 8080 ya en uso
**Solución:** 
1. Para el proceso que usa el puerto 8080
2. O edita `docker-compose.yml` y cambia el puerto (ej: "8081:8080")

### Problema: Los servicios no inician
**Solución:** Ejecuta `docker-compose logs` para ver los errores.

### Problema: "Database not initialized"
**Solución:** Ejecuta el comando de inicialización de BD del Paso 2.

---

## 🔄 Reinicio Completo (Empezar desde cero)

```powershell
# Parar y eliminar todo
docker-compose down -v

# Levantar servicios
docker-compose up -d

# Inicializar BD
docker-compose run --rm webserver airflow db init

# Crear usuario
docker-compose run --rm webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

---

## 🎯 ¡Ya estás listo!

✅ Airflow funcionando en [http://localhost:8080](http://localhost:8080)  
✅ Usuario admin creado  
✅ Base de datos inicializada  
✅ Servicios ejecutándose  

**¡Ahora puedes crear y ejecutar tus workflows en Airflow!** 🎉
