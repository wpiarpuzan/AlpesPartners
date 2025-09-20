-- ========================================
-- CAMPANIAS MICROSERVICE DATABASE SCHEMA
-- ========================================
-- Base de datos para el microservicio de Campañas
-- Gestiona campañas de marketing, contenido y tracking

-- Configuración inicial
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABLA PRINCIPAL DE CAMPAÑAS
-- ========================================

-- Tabla principal para almacenar campañas
CREATE TABLE IF NOT EXISTS campanias (
    id VARCHAR(255) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    partner_id VARCHAR(255) NOT NULL,
    brand_id VARCHAR(255),
    tipo_campania VARCHAR(50) DEFAULT 'PERFORMANCE',
    estado VARCHAR(20) DEFAULT 'BORRADOR',
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    presupuesto_total DECIMAL(15,2) DEFAULT 0.00,
    presupuesto_utilizado DECIMAL(15,2) DEFAULT 0.00,
    moneda VARCHAR(3) DEFAULT 'USD',
    objetivo VARCHAR(100),
    kpi_principal VARCHAR(50),
    meta_conversiones INTEGER DEFAULT 0,
    meta_revenue DECIMAL(15,2) DEFAULT 0.00,
    conversion_rate_target DECIMAL(5,4),
    cpc_target DECIMAL(8,2),
    cpm_target DECIMAL(8,2),
    ctr_target DECIMAL(5,4),
    categoria VARCHAR(100),
    segmento_audiencia TEXT,
    geolocalizacion JSONB, -- Países, ciudades objetivo
    dispositivos_objetivo JSONB, -- desktop, mobile, tablet
    horarios_actividad JSONB, -- Horarios de mayor actividad
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por VARCHAR(255),
    actualizado_por VARCHAR(255),
    version INTEGER DEFAULT 1,
    metadata JSONB,
    
    -- Constraints
    CONSTRAINT chk_estado_campania CHECK (estado IN ('BORRADOR', 'ACTIVA', 'PAUSADA', 'FINALIZADA', 'CANCELADA')),
    CONSTRAINT chk_tipo_campania CHECK (tipo_campania IN ('PERFORMANCE', 'BRANDING', 'AWARENESS', 'CONVERSION', 'RETENTION')),
    CONSTRAINT chk_presupuesto_positivo CHECK (presupuesto_total >= 0),
    CONSTRAINT chk_presupuesto_usado CHECK (presupuesto_utilizado >= 0 AND presupuesto_utilizado <= presupuesto_total),
    CONSTRAINT chk_fechas_validas CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT chk_metas_positivas CHECK (meta_conversiones >= 0 AND meta_revenue >= 0),
    CONSTRAINT chk_moneda_valida CHECK (moneda IN ('USD', 'COP', 'EUR', 'MXN')),
    CONSTRAINT chk_rates_validas CHECK (
        (conversion_rate_target IS NULL OR conversion_rate_target BETWEEN 0 AND 1) AND
        (ctr_target IS NULL OR ctr_target BETWEEN 0 AND 1)
    )
);