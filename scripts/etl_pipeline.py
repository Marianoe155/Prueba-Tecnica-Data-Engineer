#!/usr/bin/env python3
"""
ETL Pipeline para replicación diaria de datos a la nube
Proyecto: Data Engineer - Replicación de Base de Datos
Descripción: Extrae datos de PostgreSQL local y los replica en base de datos en la nube
Autor: Sistema ETL
Fecha: 2025-01-01
"""

import pandas as pd
import psycopg2
import sqlite3
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseReplicator:
    """Clase principal para replicación de base de datos"""
    
    def __init__(self, source_config: Dict, target_config: Dict):
        self.source_config = source_config
        self.target_config = target_config
        self.source_conn = None
        self.target_conn = None
        self.execution_log = []
        
    def connect_source(self) -> bool:
        """Conectar a la base de datos origen (PostgreSQL)"""
        try:
            self.source_conn = psycopg2.connect(**self.source_config)
            logger.info("✅ Conexión a base de datos origen establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a base origen: {e}")
            return False
    
    def connect_target(self) -> bool:
        """Conectar a la base de datos destino (SQLite para demo)"""
        try:
            # Para demo usamos SQLite, en producción sería otra base en la nube
            db_path = Path(self.target_config['database'])
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.target_conn = sqlite3.connect(str(db_path))
            logger.info("✅ Conexión a base de datos destino establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a base destino: {e}")
            return False
    
    def create_target_schema(self) -> bool:
        """Crear esquema en la base de datos destino"""
        try:
            cursor = self.target_conn.cursor()
            
            # Crear tabla dim_date
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_date (
                    dateid INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    quarter INTEGER NOT NULL,
                    quarter_name TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    month_name TEXT NOT NULL,
                    day INTEGER NOT NULL,
                    weekday INTEGER NOT NULL,
                    weekday_name TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crear tabla dim_customer_segment
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_customer_segment (
                    segment_id INTEGER PRIMARY KEY,
                    city TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crear tabla dim_product
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_product (
                    product_id INTEGER PRIMARY KEY,
                    product_type TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crear tabla fact_sales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fact_sales (
                    sales_id TEXT PRIMARY KEY,
                    date_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    segment_id INTEGER NOT NULL,
                    price_per_unit REAL NOT NULL,
                    quantity_sold INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (date_id) REFERENCES dim_date(dateid),
                    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
                    FOREIGN KEY (segment_id) REFERENCES dim_customer_segment(segment_id)
                )
            """)
            
            # Crear tabla de control de ETL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etl_control (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    last_update TEXT NOT NULL,
                    records_processed INTEGER NOT NULL,
                    execution_time_seconds REAL NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            
            # Crear índices para optimizar consultas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON fact_sales(date_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON fact_sales(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_segment ON fact_sales(segment_id)")
            
            self.target_conn.commit()
            logger.info("✅ Esquema creado en base de datos destino")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando esquema destino: {e}")
            return False
    
    def extract_table_data(self, table_name: str, schema: str = 'bi_schema') -> Optional[pd.DataFrame]:
        """Extraer datos de una tabla desde la base origen"""
        try:
            query = f"SELECT * FROM {schema}.{table_name}"
            df = pd.read_sql_query(query, self.source_conn)
            logger.info(f"✅ Extraídos {len(df)} registros de {table_name}")
            return df
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de {table_name}: {e}")
            return None
    
    def load_table_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Cargar datos en la tabla destino"""
        try:
            start_time = time.time()
            
            # Limpiar tabla destino
            cursor = self.target_conn.cursor()
            cursor.execute(f"DELETE FROM {table_name}")
            
            # Insertar datos
            df.to_sql(table_name, self.target_conn, if_exists='append', index=False)
            
            execution_time = time.time() - start_time
            
            # Registrar en tabla de control
            cursor.execute("""
                INSERT INTO etl_control 
                (table_name, last_update, records_processed, execution_time_seconds, status)
                VALUES (?, ?, ?, ?, ?)
            """, (table_name, datetime.now().isoformat(), len(df), execution_time, 'SUCCESS'))
            
            self.target_conn.commit()
            
            logger.info(f"✅ Cargados {len(df)} registros en {table_name} ({execution_time:.2f}s)")
            
            # Agregar al log de ejecución
            self.execution_log.append({
                'table': table_name,
                'records': len(df),
                'time': execution_time,
                'status': 'SUCCESS'
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando datos en {table_name}: {e}")
            
            # Registrar error en tabla de control
            cursor = self.target_conn.cursor()
            cursor.execute("""
                INSERT INTO etl_control 
                (table_name, last_update, records_processed, execution_time_seconds, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (table_name, datetime.now().isoformat(), 0, 0, 'ERROR', str(e)))
            self.target_conn.commit()
            
            self.execution_log.append({
                'table': table_name,
                'records': 0,
                'time': 0,
                'status': 'ERROR',
                'error': str(e)
            })
            
            return False
    
    def replicate_table(self, table_name: str) -> bool:
        """Replicar una tabla completa"""
        logger.info(f"🔄 Iniciando replicación de {table_name}")
        
        # Extraer datos
        df = self.extract_table_data(table_name)
        if df is None:
            return False
        
        # Cargar datos
        return self.load_table_data(df, table_name)
    
    def validate_replication(self) -> bool:
        """Validar que la replicación fue exitosa"""
        try:
            logger.info("🔍 Validando replicación...")
            
            tables = ['dim_date', 'dim_customer_segment', 'dim_product', 'fact_sales']
            validation_results = {}
            
            for table in tables:
                # Contar registros en origen
                source_cursor = self.source_conn.cursor()
                source_cursor.execute(f"SELECT COUNT(*) FROM bi_schema.{table}")
                source_count = source_cursor.fetchone()[0]
                
                # Contar registros en destino
                target_cursor = self.target_conn.cursor()
                target_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                target_count = target_cursor.fetchone()[0]
                
                validation_results[table] = {
                    'source': source_count,
                    'target': target_count,
                    'match': source_count == target_count
                }
                
                if source_count == target_count:
                    logger.info(f"✅ {table}: {source_count} registros (OK)")
                else:
                    logger.warning(f"⚠️ {table}: Origen={source_count}, Destino={target_count} (MISMATCH)")
            
            # Verificar integridad de datos
            target_cursor = self.target_conn.cursor()
            target_cursor.execute("""
                SELECT 
                    SUM(total_amount) as total_revenue,
                    COUNT(*) as total_sales,
                    AVG(total_amount) as avg_sale
                FROM fact_sales
            """)
            
            metrics = target_cursor.fetchone()
            logger.info(f"📊 Métricas destino: Revenue=${metrics[0]:,.2f}, Ventas={metrics[1]:,}, Promedio=${metrics[2]:,.2f}")
            
            all_match = all(result['match'] for result in validation_results.values())
            return all_match
            
        except Exception as e:
            logger.error(f"❌ Error en validación: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generar reporte de ejecución"""
        total_records = sum(log['records'] for log in self.execution_log if log['status'] == 'SUCCESS')
        total_time = sum(log['time'] for log in self.execution_log)
        success_count = sum(1 for log in self.execution_log if log['status'] == 'SUCCESS')
        error_count = sum(1 for log in self.execution_log if log['status'] == 'ERROR')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tables': len(self.execution_log),
            'successful_tables': success_count,
            'failed_tables': error_count,
            'total_records_processed': total_records,
            'total_execution_time': total_time,
            'tables_detail': self.execution_log
        }
        
        return report
    
    def run_full_replication(self) -> bool:
        """Ejecutar replicación completa"""
        start_time = datetime.now()
        logger.info("🚀 === INICIANDO REPLICACIÓN COMPLETA ===")
        
        try:
            # Conectar a ambas bases de datos
            if not self.connect_source():
                return False
            
            if not self.connect_target():
                return False
            
            # Crear esquema en destino
            if not self.create_target_schema():
                return False
            
            # Replicar tablas en orden (dimensiones primero)
            tables_to_replicate = [
                'dim_date',
                'dim_customer_segment', 
                'dim_product',
                'fact_sales'
            ]
            
            success = True
            for table in tables_to_replicate:
                if not self.replicate_table(table):
                    success = False
            
            # Validar replicación
            if success:
                success = self.validate_replication()
            
            # Generar reporte
            report = self.generate_report()
            
            # Guardar reporte
            report_path = Path('reports') / f"etl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if success:
                logger.info(f"✅ === REPLICACIÓN COMPLETADA EXITOSAMENTE === ({duration})")
            else:
                logger.error(f"❌ === REPLICACIÓN COMPLETADA CON ERRORES === ({duration})")
            
            logger.info(f"📄 Reporte guardado en: {report_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error crítico en replicación: {e}")
            return False
            
        finally:
            # Cerrar conexiones
            if self.source_conn:
                self.source_conn.close()
            if self.target_conn:
                self.target_conn.close()

def main():
    """Función principal"""
    # Configuración de base de datos origen (PostgreSQL)
    source_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'proyecto_data_engineer',
        'user': 'postgres',
        'password': 'postgres'  # Cambiar según configuración
    }
    
    # Configuración de base de datos destino (SQLite para demo)
    # En producción sería PostgreSQL en la nube, MySQL, etc.
    target_config = {
        'database': './cloud_mirror/data_warehouse.db'
    }
    
    # Crear replicador
    replicator = DatabaseReplicator(source_config, target_config)
    
    # Ejecutar replicación
    success = replicator.run_full_replication()
    
    if success:
        print("✅ Replicación completada exitosamente")
        return 0
    else:
        print("❌ Error en la replicación")
        return 1

if __name__ == "__main__":
    exit(main())
