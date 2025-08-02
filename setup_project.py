#!/usr/bin/env python3
"""
Script de configuración automática del proyecto Data Engineer
Proyecto: Data Engineer - Replicación de Base de Datos
Descripción: Configura automáticamente todo el entorno del proyecto
Autor: Sistema ETL
Fecha: 2025-01-01
"""

import subprocess
import sys
import os
from pathlib import Path
import psycopg2
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectSetup:
    """Clase para configurar automáticamente el proyecto"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.success_steps = []
        self.failed_steps = []
        
    def check_prerequisites(self):
        """Verificar prerrequisitos del sistema"""
        logger.info("🔍 Verificando prerrequisitos...")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            logger.info(f"✅ Python {python_version.major}.{python_version.minor} OK")
            self.success_steps.append("Python version check")
        else:
            logger.error(f"❌ Python {python_version.major}.{python_version.minor} - Se requiere Python 3.8+")
            self.failed_steps.append("Python version check")
            return False
        
        # Verificar PostgreSQL
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
                self.success_steps.append("PostgreSQL check")
            else:
                logger.error("❌ PostgreSQL no encontrado")
                self.failed_steps.append("PostgreSQL check")
                return False
        except FileNotFoundError:
            logger.error("❌ PostgreSQL no está instalado o no está en PATH")
            self.failed_steps.append("PostgreSQL check")
            return False
        
        return True
    
    def install_dependencies(self):
        """Instalar dependencias de Python"""
        logger.info("📦 Instalando dependencias...")
        
        try:
            requirements_file = self.project_root / 'requirements.txt'
            
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Dependencias instaladas correctamente")
                self.success_steps.append("Dependencies installation")
                return True
            else:
                logger.error(f"❌ Error instalando dependencias: {result.stderr}")
                self.failed_steps.append("Dependencies installation")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error instalando dependencias: {e}")
            self.failed_steps.append("Dependencies installation")
            return False
    
    def create_directories(self):
        """Crear directorios necesarios"""
        logger.info("📁 Creando directorios...")
        
        directories = [
            'logs',
            'reports', 
            'cloud_mirror',
            'backups'
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
                logger.info(f"✅ Directorio creado: {directory}")
            
            self.success_steps.append("Directory creation")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando directorios: {e}")
            self.failed_steps.append("Directory creation")
            return False
    
    def setup_database(self):
        """Configurar base de datos PostgreSQL"""
        logger.info("🗃️ Configurando base de datos...")
        
        # Configuración de conexión (ajustar según tu instalación)
        db_configs = [
            {
                'host': 'localhost',
                'port': 5432,
                'user': 'postgres',
                'password': 'postgres'  # Cambiar según tu configuración
            }
        ]
        
        for config in db_configs:
            try:
                # Intentar conexión
                conn = psycopg2.connect(
                    host=config['host'],
                    port=config['port'],
                    user=config['user'],
                    password=config['password'],
                    database='postgres'  # Base por defecto
                )
                conn.autocommit = True
                
                # Verificar si la base de datos ya existe
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM pg_database WHERE datname = 'proyecto_data_engineer'
                """)
                
                if cursor.fetchone():
                    logger.info("✅ Base de datos 'proyecto_data_engineer' ya existe")
                else:
                    # Crear base de datos
                    cursor.execute("CREATE DATABASE proyecto_data_engineer")
                    logger.info("✅ Base de datos 'proyecto_data_engineer' creada")
                
                conn.close()
                
                # Ejecutar scripts de configuración
                scripts = [
                    'database/setup/initial_setup.sql',
                    'database/setup/create_bi_schema.sql'
                ]
                
                for script in scripts:
                    script_path = self.project_root / script
                    if script_path.exists():
                        try:
                            result = subprocess.run([
                                'psql',
                                '-h', config['host'],
                                '-p', str(config['port']),
                                '-U', config['user'],
                                '-d', 'proyecto_data_engineer',
                                '-f', str(script_path)
                            ], capture_output=True, text=True, 
                            env={**os.environ, 'PGPASSWORD': config['password']})
                            
                            if result.returncode == 0:
                                logger.info(f"✅ Script ejecutado: {script}")
                            else:
                                logger.warning(f"⚠️ Advertencia ejecutando {script}: {result.stderr}")
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Error ejecutando {script}: {e}")
                
                self.success_steps.append("Database setup")
                return True
                
            except psycopg2.OperationalError as e:
                logger.warning(f"⚠️ No se pudo conectar con config {config}: {e}")
                continue
            except Exception as e:
                logger.error(f"❌ Error configurando base de datos: {e}")
                continue
        
        logger.error("❌ No se pudo configurar la base de datos con ninguna configuración")
        self.failed_steps.append("Database setup")
        return False
    
    def load_sample_data(self):
        """Cargar datos de ejemplo"""
        logger.info("📊 Cargando datos de ejemplo...")
        
        try:
            script_path = self.project_root / 'scripts' / 'load_csv_data.py'
            
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                logger.info("✅ Datos de ejemplo cargados correctamente")
                logger.info(result.stdout[-200:])  # Mostrar últimas líneas
                self.success_steps.append("Sample data loading")
                return True
            else:
                logger.error(f"❌ Error cargando datos: {result.stderr}")
                self.failed_steps.append("Sample data loading")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            self.failed_steps.append("Sample data loading")
            return False
    
    def test_etl_pipeline(self):
        """Probar el pipeline ETL"""
        logger.info("🧪 Probando pipeline ETL...")
        
        try:
            script_path = self.project_root / 'scripts' / 'etl_pipeline.py'
            
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                logger.info("✅ Pipeline ETL ejecutado correctamente")
                self.success_steps.append("ETL pipeline test")
                return True
            else:
                logger.error(f"❌ Error en pipeline ETL: {result.stderr}")
                self.failed_steps.append("ETL pipeline test")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error probando ETL: {e}")
            self.failed_steps.append("ETL pipeline test")
            return False
    
    def generate_setup_report(self):
        """Generar reporte de configuración"""
        logger.info("📄 Generando reporte de configuración...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'success_steps': self.success_steps,
            'failed_steps': self.failed_steps,
            'total_steps': len(self.success_steps) + len(self.failed_steps),
            'success_rate': len(self.success_steps) / (len(self.success_steps) + len(self.failed_steps)) * 100
        }
        
        # Guardar reporte
        report_path = self.project_root / 'setup_report.json'
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Reporte guardado en: {report_path}")
        return report
    
    def run_full_setup(self):
        """Ejecutar configuración completa"""
        start_time = datetime.now()
        logger.info("🚀 === INICIANDO CONFIGURACIÓN DEL PROYECTO ===")
        
        steps = [
            ("Verificar prerrequisitos", self.check_prerequisites),
            ("Instalar dependencias", self.install_dependencies),
            ("Crear directorios", self.create_directories),
            ("Configurar base de datos", self.setup_database),
            ("Cargar datos de ejemplo", self.load_sample_data),
            ("Probar pipeline ETL", self.test_etl_pipeline)
        ]
        
        for step_name, step_function in steps:
            logger.info(f"▶️ {step_name}...")
            success = step_function()
            if not success:
                logger.warning(f"⚠️ Paso falló: {step_name}")
        
        # Generar reporte
        report = self.generate_setup_report()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 50)
        logger.info("📊 RESUMEN DE CONFIGURACIÓN")
        logger.info("=" * 50)
        logger.info(f"✅ Pasos exitosos: {len(self.success_steps)}")
        logger.info(f"❌ Pasos fallidos: {len(self.failed_steps)}")
        logger.info(f"📈 Tasa de éxito: {report['success_rate']:.1f}%")
        logger.info(f"⏱️ Tiempo total: {duration}")
        
        if self.failed_steps:
            logger.info("\n❌ Pasos que fallaron:")
            for step in self.failed_steps:
                logger.info(f"  - {step}")
        
        logger.info("\n✅ Pasos exitosos:")
        for step in self.success_steps:
            logger.info(f"  - {step}")
        
        if len(self.failed_steps) == 0:
            logger.info("\n🎉 === CONFIGURACIÓN COMPLETADA EXITOSAMENTE ===")
            logger.info("\n📋 PRÓXIMOS PASOS:")
            logger.info("1. Revisar la documentación en docs/PROJECT_DOCUMENTATION.md")
            logger.info("2. Configurar automatización: python scripts/daily_etl_scheduler.py setup-windows")
            logger.info("3. Ejecutar ETL manualmente: python scripts/etl_pipeline.py")
            return True
        else:
            logger.info("\n⚠️ === CONFIGURACIÓN COMPLETADA CON ADVERTENCIAS ===")
            logger.info("Revisa los errores anteriores y configura manualmente los pasos fallidos.")
            return False

def main():
    """Función principal"""
    print("🔧 Configurador Automático - Proyecto Data Engineer")
    print("=" * 50)
    
    setup = ProjectSetup()
    success = setup.run_full_setup()
    
    if success:
        print("\n✅ ¡Proyecto configurado exitosamente!")
        return 0
    else:
        print("\n⚠️ Configuración completada con advertencias.")
        return 1

if __name__ == "__main__":
    exit(main())
