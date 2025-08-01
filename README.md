# Airflow Docker Setup

Este proyecto contiene una configuración completa de Apache Airflow con microservicios Docker que se puede levantar fácilmente con un solo comando.

## Estructura del Proyecto

```
.
├── docker-compose.yml    # Configuración de servicios Docker
├── Dockerfile           # Imagen personalizada de Airflow (opcional)
├── .env                # Variables de entorno
├── init-airflow.sh     # Script de inicialización
├── dags/               # Directorio para DAGs de Airflow
│   └── example_dag.py  # DAG de ejemplo
└── README.md           # Este archivo
```

## Servicios Incluidos

- **Postgres**: Base de datos para metadatos de Airflow
- **Redis**: Message broker para Celery
- **Webserver**: Interfaz web de Airflow
- **Scheduler**: Programador de tareas de Airflow

## Instalación y Uso Rápido

### 1. Levantar los servicios

```bash
docker-compose up -d
```

### 2. Inicializar la base de datos (solo la primera vez)

En Linux/Mac:
```bash
chmod +x init-airflow.sh
./init-airflow.sh
```

En Windows PowerShell:
```powershell
docker-compose run --rm webserver airflow db init
docker-compose run --rm webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

### 3. Acceder a la interfaz web

Abre tu navegador y ve a: http://localhost:8080

- **Usuario**: admin
- **Contraseña**: admin

## Comandos Útiles

### Ver logs de los servicios
```bash
docker-compose logs -f
```

### Parar los servicios
```bash
docker-compose down
```

### Parar y limpiar volúmenes (cuidado: borra la base de datos)
```bash
docker-compose down -v
```

### Ejecutar comandos de Airflow
```bash
docker-compose run --rm webserver airflow <comando>
```

## Agregar DAGs

1. Coloca tus archivos DAG en la carpeta `dags/`
2. Los DAGs se actualizarán automáticamente en la interfaz web

## Personalización

- **Variables de entorno**: Modifica el archivo `.env`
- **Configuración adicional**: Edita `docker-compose.yml`
- **Paquetes adicionales**: Modifica el `Dockerfile` y reconstruye la imagen

## Notas Importantes

- La primera vez que ejecutes el sistema, puede tardar unos minutos en descargar las imágenes
- Los datos de la base de datos se persisten en un volumen Docker
- Los DAGs se sincronizan automáticamente desde la carpeta local
