# 📊 Proyecto Data Engineer - Replicación de Base de Datos

## 📋 Descripción General

Este proyecto implementa un pipeline ETL completo para replicar datos de ventas desde una base de datos PostgreSQL local hacia una base de datos espejo en la nube, automatizando el proceso para ejecutarse diariamente.

### 🎯 Objetivos
- ✅ Crear y poblar base de datos origen con datos CSV
- ✅ Implementar replicación automática a base espejo
- ✅ Automatizar ejecución diaria del pipeline
- ✅ Documentar arquitectura y procesos

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CSV Files     │───▶│  PostgreSQL     │───▶│  Cloud Mirror   │
│                 │    │  (Source DB)    │    │  (Target DB)    │
│ • DimDate       │    │                 │    │                 │
│ • DimProduct    │    │ bi_schema       │    │ Replicated      │
│ • DimSegment    │    │ • dim_date      │    │ Tables          │
│ • FactSales     │    │ • dim_product   │    │                 │
└─────────────────┘    │ • dim_segment   │    │                 │
                       │ • fact_sales    │    │                 │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  ETL Pipeline   │
                       │                 │
                       │ • Extraction    │
                       │ • Validation    │
                       │ • Loading       │
                       │ • Monitoring    │
                       └─────────────────┘
```

## 📁 Estructura del Proyecto

```
Prueba-Tecnica-Data-Engineer/
├── 📄 README.md                    # Documentación principal
├── 📄 requirements.txt             # Dependencias Python
├── 📄 docker-compose.yml          # Configuración Docker
├── 📄 .env                        # Variables de entorno
│
├── 📁 data/                       # Datos CSV originales
│   ├── DimDate (1).csv
│   ├── DimCustomerSegment.csv
│   ├── DimProduct.csv
│   └── FactSales.csv
│
├── 📁 database/                   # Scripts de base de datos
│   ├── 📁 setup/
│   │   ├── create_database.sql    # Creación de BD principal
│   │   ├── initial_setup.sql     # Configuración inicial
│   │   └── create_bi_schema.sql   # Esquema optimizado para BI
│   ├── 📁 scripts/
│   │   ├── 📁 tables/
│   │   └── 📁 data/
│   └── 📁 docs/
│
├── 📁 scripts/                    # Scripts ETL y automatización
│   ├── load_csv_data.py          # Carga inicial de CSV
│   ├── etl_pipeline.py           # Pipeline de replicación
│   └── daily_etl_scheduler.py    # Automatización diaria
│
├── 📁 docs/                       # Documentación
│   └── PROJECT_DOCUMENTATION.md  # Este documento
│
├── 📁 logs/                       # Logs del sistema
├── 📁 reports/                    # Reportes de ejecución
└── 📁 cloud_mirror/              # Base de datos espejo
```

## 🗃️ Esquema de Base de Datos

### Base de Datos Origen: `proyecto_data_engineer`

#### Esquema: `bi_schema`

**Tablas de Dimensión:**

1. **`dim_date`** - Dimensión temporal
   ```sql
   - dateid (PK)
   - date
   - year, quarter, quarter_name
   - month, month_name
   - day, weekday, weekday_name
   ```

2. **`dim_customer_segment`** - Segmentos de cliente
   ```sql
   - segment_id (PK)
   - city
   ```

3. **`dim_product`** - Productos
   ```sql
   - product_id (PK)
   - product_type
   ```

**Tabla de Hechos:**

4. **`fact_sales`** - Transacciones de ventas
   ```sql
   - sales_id (PK)
   - date_id (FK → dim_date)
   - product_id (FK → dim_product)
   - segment_id (FK → dim_customer_segment)
   - price_per_unit
   - quantity_sold
   - total_amount (calculado)
   ```

### Vistas Analíticas

- **`vw_sales_analysis`**: Vista desnormalizada para análisis
- **`vw_monthly_metrics`**: Métricas agregadas por mes

## 🔧 Instalación y Configuración

### 1. Prerrequisitos

```bash
# Software requerido
- Python 3.8+
- PostgreSQL 12+
- Git
```

### 2. Instalación

```bash
# Clonar repositorio
git clone <repository-url>
cd Prueba-Tecnica-Data-Engineer

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

```bash
# 1. Crear base de datos
psql -U postgres -f database/setup/create_database.sql

# 2. Configurar esquema inicial
psql -U postgres -d proyecto_data_engineer -f database/setup/initial_setup.sql

# 3. Crear esquema BI
psql -U postgres -d proyecto_data_engineer -f database/setup/create_bi_schema.sql
```

### 4. Configuración de Variables de Entorno

Editar archivo `.env`:
```env
# Base de datos origen
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proyecto_data_engineer
DB_USER=postgres
DB_PASSWORD=tu_password

# Configuración ETL
ETL_SCHEDULE_TIME=02:00
LOG_LEVEL=INFO

# Notificaciones (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=tu-email@gmail.com
EMAIL_TO=admin@proyecto-data-engineer.com
```

## 🚀 Ejecución del Sistema

### 1. Carga Inicial de Datos

```bash
# Cargar datos CSV en PostgreSQL
python scripts/load_csv_data.py
```

**Salida esperada:**
```
✅ Cargados 350 registros en dim_date
✅ Cargados 20 registros en dim_customer_segment  
✅ Cargados 25 registros en dim_product
✅ Cargados 26 registros en fact_sales
📊 Revenue total: $50,847.74
```

### 2. Ejecución Manual del ETL

```bash
# Ejecutar replicación inmediatamente
python scripts/etl_pipeline.py
```

**Salida esperada:**
```
🚀 === INICIANDO REPLICACIÓN COMPLETA ===
✅ Conexión a base de datos origen establecida
✅ Conexión a base de datos destino establecida
✅ Esquema creado en base de datos destino
🔄 Iniciando replicación de dim_date
✅ Extraídos 350 registros de dim_date
✅ Cargados 350 registros en dim_date (0.45s)
...
✅ === REPLICACIÓN COMPLETADA EXITOSAMENTE ===
```

### 3. Automatización Diaria

```bash
# Iniciar scheduler (ejecuta a las 2:00 AM diariamente)
python scripts/daily_etl_scheduler.py

# Comandos adicionales
python scripts/daily_etl_scheduler.py run           # Ejecutar inmediatamente
python scripts/daily_etl_scheduler.py status       # Ver estado
python scripts/daily_etl_scheduler.py setup-windows # Configurar tarea Windows
```

## 📊 Monitoreo y Reportes

### Logs del Sistema

Los logs se guardan en:
- `etl_load.log` - Carga inicial de datos
- `etl_pipeline.log` - Ejecuciones del pipeline
- `scheduler.log` - Actividad del scheduler

### Reportes de Ejecución

Cada ejecución genera un reporte JSON en `reports/`:
```json
{
  "timestamp": "2025-01-01T02:00:00",
  "total_tables": 4,
  "successful_tables": 4,
  "failed_tables": 0,
  "total_records_processed": 421,
  "total_execution_time": 2.34,
  "tables_detail": [...]
}
```

### Métricas de Validación

El sistema valida automáticamente:
- ✅ Integridad referencial
- ✅ Conteo de registros origen vs destino
- ✅ Métricas de negocio (revenue, ventas)

## 🔍 Consultas de Análisis

### Consultas Básicas

```sql
-- Revenue total por mes
SELECT 
    year, month_name,
    SUM(total_amount) as monthly_revenue
FROM vw_sales_analysis 
GROUP BY year, month_name 
ORDER BY year, month;

-- Top productos por ventas
SELECT 
    product_type,
    SUM(quantity_sold) as total_quantity,
    SUM(total_amount) as total_revenue
FROM vw_sales_analysis
GROUP BY product_type
ORDER BY total_revenue DESC;

-- Ventas por ciudad
SELECT 
    city,
    COUNT(*) as transactions,
    SUM(total_amount) as revenue
FROM vw_sales_analysis
GROUP BY city
ORDER BY revenue DESC;
```

### Dashboard Metrics

```sql
-- KPIs principales
SELECT 
    COUNT(*) as total_transactions,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction,
    COUNT(DISTINCT product_type) as unique_products,
    COUNT(DISTINCT city) as unique_cities
FROM vw_sales_analysis;
```

## 🌐 Acceso a Base de Datos Espejo

### Información de Conexión

**Base de Datos Espejo (SQLite para demo):**
- **Ubicación**: `./cloud_mirror/data_warehouse.db`
- **Tipo**: SQLite (en producción sería PostgreSQL/MySQL en la nube)
- **Acceso**: Directo via Python/SQLite tools

### Conexión Programática

```python
import sqlite3

# Conectar a base espejo
conn = sqlite3.connect('./cloud_mirror/data_warehouse.db')

# Consultar datos
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM fact_sales")
print(f"Total ventas: {cursor.fetchone()[0]}")

conn.close()
```

### Herramientas Recomendadas

- **DB Browser for SQLite** - GUI para SQLite
- **DBeaver** - Cliente universal de BD
- **Python pandas** - Análisis de datos

## 🔧 Mantenimiento

### Tareas Regulares

1. **Monitoreo de Logs**
   ```bash
   # Ver últimas ejecuciones
   tail -f etl_pipeline.log
   
   # Verificar errores
   grep "ERROR" *.log
   ```

2. **Limpieza de Archivos**
   ```bash
   # Limpiar logs antiguos (>30 días)
   find logs/ -name "*.log" -mtime +30 -delete
   
   # Limpiar reportes antiguos (>90 días)  
   find reports/ -name "*.json" -mtime +90 -delete
   ```

3. **Backup de Base Espejo**
   ```bash
   # Backup automático
   cp cloud_mirror/data_warehouse.db backups/warehouse_$(date +%Y%m%d).db
   ```

### Solución de Problemas

**Error de Conexión a BD:**
```bash
# Verificar servicio PostgreSQL
pg_ctl status

# Verificar conectividad
psql -h localhost -U postgres -d proyecto_data_engineer
```

**ETL Falla:**
```bash
# Verificar logs
cat etl_pipeline.log | tail -50

# Ejecutar en modo debug
python scripts/etl_pipeline.py --debug
```

## 📈 Mejoras Futuras

### Funcionalidades Pendientes

1. **Escalabilidad**
   - Implementar particionado de tablas
   - Optimizar índices para grandes volúmenes
   - Paralelización de procesos ETL

2. **Monitoreo Avanzado**
   - Dashboard web en tiempo real
   - Alertas proactivas por Slack/Teams
   - Métricas de performance detalladas

3. **Seguridad**
   - Encriptación de datos en tránsito
   - Autenticación con certificados
   - Auditoría de accesos

4. **Cloud Native**
   - Migración a AWS RDS/Azure SQL
   - Uso de servicios managed (AWS Glue, Azure Data Factory)
   - Containerización con Kubernetes

## 👥 Contacto y Soporte

**Desarrollador:** Sistema ETL  
**Email:** admin@proyecto-data-engineer.com  
**Documentación:** Este archivo  
**Repositorio:** [GitHub URL]

---

*Documentación generada automáticamente - Última actualización: 2025-01-01*
