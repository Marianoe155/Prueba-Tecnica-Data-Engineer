-- ============================================
-- CREACIÓN DEL ESQUEMA PARA BUSINESS INTELLIGENCE
-- Proyecto: Data Engineer - Replicación de Base de Datos
-- Descripción: Esquema optimizado para análisis de ventas
-- ============================================

-- Conectarse a la base de datos
-- \c proyecto_data_engineer;

-- Crear esquema específico para BI
CREATE SCHEMA IF NOT EXISTS bi_schema;
SET search_path TO bi_schema, public;

-- ============================================
-- TABLA DE DIMENSIÓN: FECHAS
-- ============================================
CREATE TABLE IF NOT EXISTS dim_date (
    dateid INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    quarter_name VARCHAR(2) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    weekday INTEGER NOT NULL,
    weekday_name VARCHAR(20) NOT NULL,
    
    -- Índices para optimizar consultas
    CONSTRAINT chk_quarter CHECK (quarter BETWEEN 1 AND 4),
    CONSTRAINT chk_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_day CHECK (day BETWEEN 1 AND 31),
    CONSTRAINT chk_weekday CHECK (weekday BETWEEN 1 AND 7)
);

-- Crear índices para optimizar consultas de BI
CREATE INDEX IF NOT EXISTS idx_dim_date_year ON dim_date(year);
CREATE INDEX IF NOT EXISTS idx_dim_date_quarter ON dim_date(quarter);
CREATE INDEX IF NOT EXISTS idx_dim_date_month ON dim_date(month);
CREATE INDEX IF NOT EXISTS idx_dim_date_date ON dim_date(date);

-- ============================================
-- TABLA DE DIMENSIÓN: SEGMENTOS DE CLIENTE
-- ============================================
CREATE TABLE IF NOT EXISTS dim_customer_segment (
    segment_id INTEGER PRIMARY KEY,
    city VARCHAR(100) NOT NULL
);

-- Crear índice para búsquedas por ciudad
CREATE INDEX IF NOT EXISTS idx_dim_segment_city ON dim_customer_segment(city);

-- ============================================
-- TABLA DE DIMENSIÓN: PRODUCTOS
-- ============================================
CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    product_type VARCHAR(100) NOT NULL
);

-- Crear índice para búsquedas por tipo de producto
CREATE INDEX IF NOT EXISTS idx_dim_product_type ON dim_product(product_type);

-- ============================================
-- TABLA DE HECHOS: VENTAS
-- ============================================
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id VARCHAR(20) PRIMARY KEY,
    date_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    segment_id INTEGER NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    quantity_sold INTEGER NOT NULL,
    total_amount DECIMAL(12,2) GENERATED ALWAYS AS (price_per_unit * quantity_sold) STORED,
    
    -- Claves foráneas
    CONSTRAINT fk_sales_date FOREIGN KEY (date_id) REFERENCES dim_date(dateid),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    CONSTRAINT fk_sales_segment FOREIGN KEY (segment_id) REFERENCES dim_customer_segment(segment_id),
    
    -- Restricciones de integridad
    CONSTRAINT chk_price_positive CHECK (price_per_unit > 0),
    CONSTRAINT chk_quantity_positive CHECK (quantity_sold > 0)
);

-- Crear índices para optimizar consultas de BI
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_sales(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_segment ON fact_sales(segment_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_total ON fact_sales(total_amount);

-- ============================================
-- VISTAS PARA ANÁLISIS COMÚN
-- ============================================

-- Vista consolidada de ventas con todas las dimensiones
CREATE OR REPLACE VIEW vw_sales_analysis AS
SELECT 
    fs.sales_id,
    fs.total_amount,
    fs.quantity_sold,
    fs.price_per_unit,
    
    -- Dimensión fecha
    dd.date,
    dd.year,
    dd.quarter_name,
    dd.month_name,
    dd.weekday_name,
    
    -- Dimensión producto
    dp.product_type,
    
    -- Dimensión segmento
    dcs.city
FROM fact_sales fs
JOIN dim_date dd ON fs.date_id = dd.dateid
JOIN dim_product dp ON fs.product_id = dp.product_id
JOIN dim_customer_segment dcs ON fs.segment_id = dcs.segment_id;

-- Vista de métricas agregadas por mes
CREATE OR REPLACE VIEW vw_monthly_metrics AS
SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(*) as total_transactions,
    SUM(fs.quantity_sold) as total_quantity,
    SUM(fs.total_amount) as total_revenue,
    AVG(fs.total_amount) as avg_transaction_value,
    COUNT(DISTINCT fs.product_id) as unique_products,
    COUNT(DISTINCT fs.segment_id) as unique_segments
FROM fact_sales fs
JOIN dim_date dd ON fs.date_id = dd.dateid
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;

-- ============================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ============================================

COMMENT ON SCHEMA bi_schema IS 'Esquema optimizado para Business Intelligence y análisis de ventas';

COMMENT ON TABLE dim_date IS 'Dimensión de fechas con atributos para análisis temporal';
COMMENT ON TABLE dim_customer_segment IS 'Dimensión de segmentos de clientes por ciudad';
COMMENT ON TABLE dim_product IS 'Dimensión de productos por tipo';
COMMENT ON TABLE fact_sales IS 'Tabla de hechos con transacciones de ventas';

COMMENT ON VIEW vw_sales_analysis IS 'Vista desnormalizada para análisis completo de ventas';
COMMENT ON VIEW vw_monthly_metrics IS 'Métricas agregadas por mes para dashboards';

-- ============================================
-- PERMISOS
-- ============================================

-- Otorgar permisos al usuario de la aplicación
GRANT USAGE ON SCHEMA bi_schema TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA bi_schema TO app_user;
GRANT SELECT ON ALL VIEWS IN SCHEMA bi_schema TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA bi_schema TO app_user;

-- Mensaje de confirmación
SELECT 'Esquema BI creado exitosamente con tablas optimizadas para análisis de ventas' as status;
