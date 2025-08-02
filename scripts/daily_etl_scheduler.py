#!/usr/bin/env python3
"""
Automatización diaria del pipeline ETL
Proyecto: Data Engineer - Replicación de Base de Datos
Descripción: Scheduler para ejecutar la replicación diaria automáticamente
Autor: Sistema ETL
Fecha: 2025-01-01
"""

import schedule
import time
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ETLScheduler:
    """Clase para automatizar la ejecución del ETL"""
    
    def __init__(self, etl_script_path: str, notification_config: dict = None):
        self.etl_script_path = Path(etl_script_path)
        self.notification_config = notification_config or {}
        self.last_execution = None
        self.execution_history = []
        
    def run_etl_job(self):
        """Ejecutar el trabajo ETL"""
        start_time = datetime.now()
        logger.info(f"🚀 Iniciando ejecución ETL programada - {start_time}")
        
        try:
            # Ejecutar el script ETL
            result = subprocess.run([
                sys.executable, str(self.etl_script_path)
            ], capture_output=True, text=True, timeout=3600)  # 1 hora timeout
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            execution_record = {
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            self.execution_history.append(execution_record)
            self.last_execution = execution_record
            
            # Guardar historial
            self._save_execution_history()
            
            if result.returncode == 0:
                logger.info(f"✅ ETL completado exitosamente en {duration}")
                self._send_notification("SUCCESS", execution_record)
            else:
                logger.error(f"❌ ETL falló con código {result.returncode}")
                logger.error(f"Error: {result.stderr}")
                self._send_notification("ERROR", execution_record)
                
        except subprocess.TimeoutExpired:
            logger.error("❌ ETL excedió el tiempo límite (1 hora)")
            execution_record = {
                'timestamp': start_time.isoformat(),
                'duration_seconds': 3600,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Timeout after 1 hour',
                'success': False
            }
            self.execution_history.append(execution_record)
            self._send_notification("TIMEOUT", execution_record)
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando ETL: {e}")
            execution_record = {
                'timestamp': start_time.isoformat(),
                'duration_seconds': 0,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
            self.execution_history.append(execution_record)
            self._send_notification("EXCEPTION", execution_record)
    
    def _save_execution_history(self):
        """Guardar historial de ejecuciones"""
        try:
            history_file = Path('logs') / 'execution_history.json'
            history_file.parent.mkdir(exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")
    
    def _send_notification(self, status: str, execution_record: dict):
        """Enviar notificación por email (opcional)"""
        if not self.notification_config.get('enabled', False):
            return
        
        try:
            # Configurar mensaje
            msg = MimeMultipart()
            msg['From'] = self.notification_config['from_email']
            msg['To'] = self.notification_config['to_email']
            
            if status == "SUCCESS":
                msg['Subject'] = "✅ ETL Pipeline - Ejecución Exitosa"
                body = f"""
                El pipeline ETL se ejecutó exitosamente.
                
                Detalles:
                - Timestamp: {execution_record['timestamp']}
                - Duración: {execution_record['duration_seconds']:.2f} segundos
                - Estado: Completado
                
                Logs:
                {execution_record['stdout'][:500]}...
                """
            else:
                msg['Subject'] = f"❌ ETL Pipeline - Error ({status})"
                body = f"""
                El pipeline ETL falló durante la ejecución.
                
                Detalles:
                - Timestamp: {execution_record['timestamp']}
                - Duración: {execution_record['duration_seconds']:.2f} segundos
                - Código de retorno: {execution_record['return_code']}
                - Estado: {status}
                
                Error:
                {execution_record['stderr'][:500]}...
                """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(self.notification_config['smtp_server'], 
                                self.notification_config['smtp_port'])
            server.starttls()
            server.login(self.notification_config['username'], 
                        self.notification_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.notification_config['from_email'], 
                          self.notification_config['to_email'], text)
            server.quit()
            
            logger.info(f"📧 Notificación enviada: {status}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
    
    def get_status_report(self) -> dict:
        """Obtener reporte de estado del scheduler"""
        if not self.execution_history:
            return {
                'status': 'NO_EXECUTIONS',
                'message': 'No se han ejecutado trabajos ETL aún'
            }
        
        recent_executions = self.execution_history[-10:]  # Últimas 10 ejecuciones
        success_count = sum(1 for exec in recent_executions if exec['success'])
        
        return {
            'status': 'ACTIVE',
            'total_executions': len(self.execution_history),
            'recent_success_rate': f"{success_count}/{len(recent_executions)}",
            'last_execution': self.last_execution,
            'next_scheduled': schedule.next_run()
        }
    
    def start_scheduler(self, schedule_time: str = "02:00"):
        """Iniciar el scheduler"""
        logger.info(f"📅 Configurando ejecución diaria a las {schedule_time}")
        
        # Programar ejecución diaria
        schedule.every().day.at(schedule_time).do(self.run_etl_job)
        
        # También permitir ejecución manual cada hora para testing
        # schedule.every().hour.do(self.run_etl_job)  # Descomenta para testing
        
        logger.info("🔄 Scheduler iniciado. Presiona Ctrl+C para detener.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error en scheduler: {e}")

def create_windows_task():
    """Crear tarea programada en Windows"""
    script_path = Path(__file__).absolute()
    python_path = sys.executable
    
    # Comando para crear tarea en Windows
    task_command = f'''
    schtasks /create /tn "ETL_Data_Engineer_Daily" /tr "{python_path} {script_path}" /sc daily /st 02:00 /f
    '''
    
    print("Para crear una tarea programada en Windows, ejecuta:")
    print(task_command)
    print("\nO usa el Programador de tareas de Windows manualmente.")

def create_linux_cron():
    """Mostrar instrucciones para cron en Linux"""
    script_path = Path(__file__).absolute()
    python_path = sys.executable
    
    cron_entry = f"0 2 * * * {python_path} {script_path}"
    
    print("Para programar en Linux/macOS, agrega esta línea al crontab:")
    print(f"crontab -e")
    print(f"{cron_entry}")

def main():
    """Función principal"""
    # Configuración del ETL script
    etl_script = Path(__file__).parent / "etl_pipeline.py"
    
    # Configuración de notificaciones (opcional)
    notification_config = {
        'enabled': False,  # Cambiar a True para habilitar notificaciones
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'from_email': 'tu-email@gmail.com',
        'to_email': 'admin@proyecto-data-engineer.com',
        'username': 'tu-email@gmail.com',
        'password': 'tu-password-app'  # Usar App Password para Gmail
    }
    
    # Crear scheduler
    scheduler = ETLScheduler(str(etl_script), notification_config)
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "run":
            # Ejecutar ETL inmediatamente
            logger.info("Ejecutando ETL manualmente...")
            scheduler.run_etl_job()
            
        elif command == "status":
            # Mostrar estado
            status = scheduler.get_status_report()
            print(json.dumps(status, indent=2, default=str))
            
        elif command == "setup-windows":
            # Mostrar instrucciones para Windows
            create_windows_task()
            
        elif command == "setup-linux":
            # Mostrar instrucciones para Linux
            create_linux_cron()
            
        else:
            print("Comandos disponibles:")
            print("  run           - Ejecutar ETL inmediatamente")
            print("  status        - Mostrar estado del scheduler")
            print("  setup-windows - Instrucciones para Windows Task Scheduler")
            print("  setup-linux   - Instrucciones para Cron (Linux/macOS)")
            
    else:
        # Iniciar scheduler en modo daemon
        scheduler.start_scheduler()

if __name__ == "__main__":
    main()
