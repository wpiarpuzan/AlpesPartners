-- ========================================
-- PAGOS MICROSERVICE DATABASE SCHEMA
-- ========================================
-- Base de datos para el microservicio de Pagos
-- Gestiona payouts, transacciones y medios de pago

-- Configuración inicial
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABLA PRINCIPAL DE PAYOUTS
-- ========================================

-- Tabla principal para almacenar payouts a partners
CREATE TABLE IF NOT EXISTS payouts (
    id VARCHAR(255) PRIMARY KEY,
    partner_id VARCHAR(255) NOT NULL,
    cycle_id VARCHAR(255) NOT NULL,
    monto_total DECIMAL(15,2) DEFAULT 0.00,
    moneda VARCHAR(3) DEFAULT 'USD',
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_procesamiento TIMESTAMP,
    fecha_completado TIMESTAMP,
    confirmation_id VARCHAR(255),
    failure_reason TEXT,
    payment_method_type VARCHAR(50),
    payment_method_mask VARCHAR(50),
    processed_at TIMESTAMP,
    completed_at TIMESTAMP,
    fee_amount DECIMAL(15,2) DEFAULT 0.00,
    net_amount DECIMAL(15,2),
    currency_exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
    banco_destino VARCHAR(100),
    cuenta_destino VARCHAR(50),
    referencia_externa VARCHAR(255),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_estado_payout CHECK (estado IN ('PENDIENTE', 'CALCULADO', 'CONFIRMADO', 'RECHAZADO', 'EN_PROCESO', 'EXITOSO', 'FALLIDO')),
    CONSTRAINT chk_monto_positivo CHECK (monto_total >= 0),
    CONSTRAINT chk_fee_positivo CHECK (fee_amount >= 0),
    CONSTRAINT chk_moneda_valida CHECK (moneda IN ('USD', 'COP', 'EUR', 'MXN')),
    CONSTRAINT chk_exchange_rate CHECK (currency_exchange_rate > 0)
);

-- ========================================
-- TABLA DE TRANSACCIONES
-- ========================================

-- Tabla para almacenar transacciones que componen payouts
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(255) PRIMARY KEY,
    partner_id VARCHAR(255) NOT NULL,
    brand_id VARCHAR(255),
    payout_id VARCHAR(255),
    comision_valor DECIMAL(15,2) DEFAULT 0.00,
    comision_moneda VARCHAR(3) DEFAULT 'USD',
    event_type VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_reference VARCHAR(255),
    original_amount DECIMAL(15,2),
    original_currency VARCHAR(3),
    fee_percentage DECIMAL(5,4),
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    net_commission DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (payout_id) REFERENCES payouts(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_comision_positiva CHECK (comision_valor >= 0),
    CONSTRAINT chk_status_transaction CHECK (status IN ('ACTIVE', 'CANCELLED', 'REFUNDED')),
    CONSTRAINT chk_fee_percentage CHECK (fee_percentage >= 0 AND fee_percentage <= 1)
);