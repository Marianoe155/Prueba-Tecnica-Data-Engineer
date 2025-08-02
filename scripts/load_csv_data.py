#!/usr/bin/env python3
"""
Script para cargar datos CSV en la base de datos PostgreSQL
Proyecto: Data Engineer - Replicación de Base de Datos
Autor: Sistema ETL
Fecha: 2025-01-01
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_load.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CSVDataLoader:
    """Clase para cargar datos CSV en PostgreSQL"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.data_path = Path(__file__).parent.parent / 'data'
        
    def connect_db(self):
        """Establecer conexión con la base de datos"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = False
            logger.info("Conexión a la base de datos establecida")
            return True
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            return False
    
    def close_connection(self):
        """Cerrar conexión con la base de datos"""
        if self.connection:
            self.connection.close()
            logger.info("Conexión cerrada")
    
    def load_dim_date(self):
        """Cargar dimensión de fechas"""
        try:
            csv_file = self.data_path / 'DimDate (1).csv'
            df = pd.read_csv(csv_file)
            
            # Limpiar y preparar datos
            df.columns = df.columns.str.lower()
            df['date'] = pd.to_datetime(df['date'])
            
            # Preparar datos para inserción
            data_tuples = [
                (
                    row['dateid'],
                    row['date'].date(),
                    row['year'],
                    row['quarter'],
                    row['quartername'],
                    row['month'],
                    row['monthname'],
                    row['day'],
                    row['weekday'],
                    row['weekdayname']
                )
                for _, row in df.iterrows()
            ]
            
            cursor = self.connection.cursor()
            
            # Limpiar tabla antes de insertar
            cursor.execute("TRUNCATE TABLE bi_schema.dim_date CASCADE")
            
            # Insertar datos
            insert_query = """
                INSERT INTO bi_schema.dim_date 
                (dateid, date, year, quarter, quarter_name, month, month_name, day, weekday, weekday_name)
                VALUES %s
            """
            
            execute_values(cursor, insert_query, data_tuples, template=None, page_size=100)
            self.connection.commit()
            
            logger.info(f"Cargados {len(data_tuples)} registros en dim_date")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando dim_date: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def load_dim_customer_segment(self):
        """Cargar dimensión de segmentos de cliente"""
        try:
            csv_file = self.data_path / 'DimCustomerSegment.csv'
            df = pd.read_csv(csv_file)
            
            # Limpiar y preparar datos
            df.columns = df.columns.str.lower()
            
            # Preparar datos para inserción
            data_tuples = [
                (row['segmentid'], row['city'])
                for _, row in df.iterrows()
            ]
            
            cursor = self.connection.cursor()
            
            # Limpiar tabla antes de insertar
            cursor.execute("TRUNCATE TABLE bi_schema.dim_customer_segment CASCADE")
            
            # Insertar datos
            insert_query = """
                INSERT INTO bi_schema.dim_customer_segment (segment_id, city)
                VALUES %s
            """
            
            execute_values(cursor, insert_query, data_tuples, template=None, page_size=100)
            self.connection.commit()
            
            logger.info(f"Cargados {len(data_tuples)} registros en dim_customer_segment")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando dim_customer_segment: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def load_dim_product(self):
        """Cargar dimensión de productos"""
        try:
            csv_file = self.data_path / 'DimProduct.csv'
            df = pd.read_csv(csv_file)
            
            # Limpiar y preparar datos
            df.columns = df.columns.str.lower()
            
            # Preparar datos para inserción
            data_tuples = [
                (row['productid'], row['producttype'])
                for _, row in df.iterrows()
            ]
            
            cursor = self.connection.cursor()
            
            # Limpiar tabla antes de insertar
            cursor.execute("TRUNCATE TABLE bi_schema.dim_product CASCADE")
            
            # Insertar datos
            insert_query = """
                INSERT INTO bi_schema.dim_product (product_id, product_type)
                VALUES %s
            """
            
            execute_values(cursor, insert_query, data_tuples, template=None, page_size=100)
            self.connection.commit()
            
            logger.info(f"Cargados {len(data_tuples)} registros en dim_product")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando dim_product: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def load_fact_sales(self):
        """Cargar tabla de hechos de ventas"""
        try:
            csv_file = self.data_path / 'FactSales.csv'
            df = pd.read_csv(csv_file)
            
            # Limpiar y preparar datos
            df.columns = df.columns.str.lower()
            
            # Preparar datos para inserción
            data_tuples = [
                (
                    row['salesid'],
                    row['dateid'],
                    row['productid'],
                    row['segmentid'],
                    float(row['price_perunit']),
                    int(row['quantitysold'])
                )
                for _, row in df.iterrows()
            ]
            
            cursor = self.connection.cursor()
            
            # Limpiar tabla antes de insertar
            cursor.execute("TRUNCATE TABLE bi_schema.fact_sales CASCADE")
            
            # Insertar datos
            insert_query = """
                INSERT INTO bi_schema.fact_sales 
                (sales_id, date_id, product_id, segment_id, price_per_unit, quantity_sold)
                VALUES %s
            """
            
            execute_values(cursor, insert_query, data_tuples, template=None, page_size=100)
            self.connection.commit()
            
            logger.info(f"Cargados {len(data_tuples)} registros en fact_sales")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando fact_sales: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def validate_data(self):
        """Validar integridad de los datos cargados"""
        try:
            cursor = self.connection.cursor()
            
            # Contar registros en cada tabla
            tables = ['dim_date', 'dim_customer_segment', 'dim_product', 'fact_sales']
            counts = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM bi_schema.{table}")
                counts[table] = cursor.fetchone()[0]
            
            logger.info("=== RESUMEN DE CARGA ===")
            for table, count in counts.items():
                logger.info(f"{table}: {count} registros")
            
            # Validar integridad referencial
            cursor.execute("""
                SELECT COUNT(*) as sales_without_date
                FROM bi_schema.fact_sales fs
                LEFT JOIN bi_schema.dim_date dd ON fs.date_id = dd.dateid
                WHERE dd.dateid IS NULL
            """)
            
            orphan_dates = cursor.fetchone()[0]
            if orphan_dates > 0:
                logger.warning(f"Encontradas {orphan_dates} ventas sin fecha válida")
            
            cursor.execute("""
                SELECT COUNT(*) as sales_without_product
                FROM bi_schema.fact_sales fs
                LEFT JOIN bi_schema.dim_product dp ON fs.product_id = dp.product_id
                WHERE dp.product_id IS NULL
            """)
            
            orphan_products = cursor.fetchone()[0]
            if orphan_products > 0:
                logger.warning(f"Encontradas {orphan_products} ventas sin producto válido")
            
            cursor.execute("""
                SELECT COUNT(*) as sales_without_segment
                FROM bi_schema.fact_sales fs
                LEFT JOIN bi_schema.dim_customer_segment dcs ON fs.segment_id = dcs.segment_id
                WHERE dcs.segment_id IS NULL
            """)
            
            orphan_segments = cursor.fetchone()[0]
            if orphan_segments > 0:
                logger.warning(f"Encontradas {orphan_segments} ventas sin segmento válido")
            
            # Mostrar algunas métricas básicas
            cursor.execute("""
                SELECT 
                    SUM(total_amount) as revenue_total,
                    AVG(total_amount) as revenue_avg,
                    SUM(quantity_sold) as quantity_total
                FROM bi_schema.fact_sales
            """)
            
            metrics = cursor.fetchone()
            logger.info(f"Revenue total: ${metrics[0]:,.2f}")
            logger.info(f"Revenue promedio: ${metrics[1]:,.2f}")
            logger.info(f"Cantidad total vendida: {metrics[2]:,}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos: {e}")
            return False
    
    def run_full_load(self):
        """Ejecutar carga completa de todos los datos"""
        start_time = datetime.now()
        logger.info("=== INICIANDO CARGA DE DATOS CSV ===")
        
        if not self.connect_db():
            return False
        
        try:
            # Cargar dimensiones primero
            success = True
            success &= self.load_dim_date()
            success &= self.load_dim_customer_segment()
            success &= self.load_dim_product()
            
            # Cargar tabla de hechos
            success &= self.load_fact_sales()
            
            # Validar datos
            if success:
                success &= self.validate_data()
            
            if success:
                logger.info("=== CARGA COMPLETADA EXITOSAMENTE ===")
            else:
                logger.error("=== CARGA COMPLETADA CON ERRORES ===")
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"Tiempo total de ejecución: {duration}")
            
            return success
            
        finally:
            self.close_connection()

def main():
    """Función principal"""
    # Configuración de la base de datos
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'proyecto_data_engineer',
        'user': 'postgres',  # Cambiar según tu configuración
        'password': 'postgres'  # Cambiar según tu configuración
    }
    
    # Crear instancia del cargador
    loader = CSVDataLoader(db_config)
    
    # Ejecutar carga
    success = loader.run_full_load()
    
    if success:
        print("✅ Datos cargados exitosamente")
        return 0
    else:
        print("❌ Error en la carga de datos")
        return 1

if __name__ == "__main__":
    exit(main())
