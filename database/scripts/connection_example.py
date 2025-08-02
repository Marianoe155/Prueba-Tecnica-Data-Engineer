#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de conexión a PostgreSQL desde Python
==============================================

Este archivo muestra cómo conectarse a la base de datos PostgreSQL
desde una aplicación Python usando psycopg2.

Requisitos:
- pip install psycopg2-binary
- PostgreSQL instalado y configurado
- Base de datos 'proyecto_data_engineer' creada
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE CONEXIÓN
# ============================================

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'proyecto_data_engineer',
    'user': 'app_user',  # o 'postgres' para administración
    'password': 'app_password_2024'  # Cambiar por tu contraseña real
}

# ============================================
# FUNCIONES DE CONEXIÓN
# ============================================

def crear_conexion():
    """
    Crea una conexión a la base de datos PostgreSQL
    
    Returns:
        connection: Objeto de conexión a la base de datos
    """
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexión exitosa a PostgreSQL")
        return conexion
    except psycopg2.Error as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        return None

def ejecutar_consulta(query, parametros=None, fetch_all=True):
    """
    Ejecuta una consulta SQL y retorna los resultados
    
    Args:
        query (str): Consulta SQL a ejecutar
        parametros (tuple): Parámetros para la consulta (opcional)
        fetch_all (bool): Si True, retorna todos los resultados
        
    Returns:
        list: Resultados de la consulta
    """
    conexion = crear_conexion()
    if not conexion:
        return None
    
    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, parametros)
            
            if fetch_all:
                resultados = cursor.fetchall()
            else:
                resultados = cursor.fetchone()
                
            conexion.commit()
            return resultados
            
    except psycopg2.Error as e:
        print(f"❌ Error al ejecutar consulta: {e}")
        conexion.rollback()
        return None
    finally:
        conexion.close()

# ============================================
# FUNCIONES DE EJEMPLO
# ============================================

def obtener_usuarios():
    """Obtiene todos los usuarios activos"""
    query = """
    SELECT id, nombre, email, fecha_creacion, activo 
    FROM app_schema.usuarios 
    WHERE activo = true 
    ORDER BY fecha_creacion DESC
    """
    return ejecutar_consulta(query)

def crear_usuario(nombre, email):
    """
    Crea un nuevo usuario
    
    Args:
        nombre (str): Nombre del usuario
        email (str): Email del usuario
        
    Returns:
        dict: Información del usuario creado
    """
    query = """
    INSERT INTO app_schema.usuarios (nombre, email) 
    VALUES (%s, %s) 
    RETURNING id, nombre, email, fecha_creacion
    """
    return ejecutar_consulta(query, (nombre, email), fetch_all=False)

def obtener_productos_por_categoria(categoria):
    """
    Obtiene productos por categoría
    
    Args:
        categoria (str): Categoría de productos
        
    Returns:
        list: Lista de productos
    """
    query = """
    SELECT id, nombre, descripcion, precio, stock, categoria 
    FROM app_schema.productos 
    WHERE categoria = %s AND activo = true
    ORDER BY nombre
    """
    return ejecutar_consulta(query, (categoria,))

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    query = """
    SELECT 
        (SELECT COUNT(*) FROM app_schema.usuarios WHERE activo = true) as usuarios_activos,
        (SELECT COUNT(*) FROM app_schema.productos WHERE activo = true) as productos_activos,
        (SELECT COUNT(*) FROM app_schema.pedidos) as total_pedidos,
        (SELECT COALESCE(SUM(total), 0) FROM app_schema.pedidos WHERE estado = 'completado') as ventas_totales
    """
    return ejecutar_consulta(query, fetch_all=False)

def registrar_log(usuario_id, accion, descripcion, ip_address='127.0.0.1'):
    """
    Registra una acción en los logs del sistema
    
    Args:
        usuario_id (int): ID del usuario
        accion (str): Tipo de acción
        descripcion (str): Descripción de la acción
        ip_address (str): Dirección IP
    """
    query = """
    INSERT INTO app_schema.logs_sistema (usuario_id, accion, descripcion, ip_address)
    VALUES (%s, %s, %s, %s)
    """
    return ejecutar_consulta(query, (usuario_id, accion, descripcion, ip_address))

# ============================================
# FUNCIÓN PRINCIPAL DE EJEMPLO
# ============================================

def main():
    """Función principal que demuestra el uso de las funciones"""
    print("🚀 Iniciando ejemplo de conexión a PostgreSQL")
    print("=" * 50)
    
    # Probar conexión
    conexion = crear_conexion()
    if not conexion:
        print("❌ No se pudo establecer conexión. Verifica la configuración.")
        return
    conexion.close()
    
    # Obtener usuarios
    print("\n👥 Usuarios en el sistema:")
    usuarios = obtener_usuarios()
    if usuarios:
        for usuario in usuarios:
            print(f"  - {usuario['nombre']} ({usuario['email']})")
    else:
        print("  No hay usuarios registrados")
    
    # Obtener productos de una categoría
    print("\n💻 Productos en categoría 'Electrónicos':")
    productos = obtener_productos_por_categoria('Electrónicos')
    if productos:
        for producto in productos:
            print(f"  - {producto['nombre']}: ${producto['precio']} (Stock: {producto['stock']})")
    else:
        print("  No hay productos en esta categoría")
    
    # Estadísticas generales
    print("\n📊 Estadísticas del sistema:")
    stats = obtener_estadisticas_generales()
    if stats:
        print(f"  - Usuarios activos: {stats['usuarios_activos']}")
        print(f"  - Productos activos: {stats['productos_activos']}")
        print(f"  - Total pedidos: {stats['total_pedidos']}")
        print(f"  - Ventas totales: ${stats['ventas_totales']}")
    
    # Ejemplo de crear usuario (comentado para evitar duplicados)
    """
    print("\n➕ Creando nuevo usuario:")
    nuevo_usuario = crear_usuario("Test Usuario", "test@ejemplo.com")
    if nuevo_usuario:
        print(f"  Usuario creado: {nuevo_usuario['nombre']}")
        
        # Registrar la acción en logs
        registrar_log(nuevo_usuario['id'], 'registro', 'Usuario creado desde script Python')
    """
    
    print("\n✅ Ejemplo completado exitosamente")

# ============================================
# EJECUTAR EJEMPLO
# ============================================

if __name__ == "__main__":
    main()
