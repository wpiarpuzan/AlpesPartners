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

-- ========================================
-- TABLA DE MÉTODOS DE PAGO
-- ========================================

-- Tabla para almacenar información detallada de métodos de pago
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    payout_id VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    mascara VARCHAR(50),
    banco VARCHAR(100),
    numero_cuenta VARCHAR(50),
    tipo_cuenta VARCHAR(20), -- AHORROS, CORRIENTE
    titular VARCHAR(255),
    documento_titular VARCHAR(50),
    es_activo BOOLEAN DEFAULT TRUE,
    fecha_verificacion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (payout_id) REFERENCES payouts(id) ON DELETE CASCADE,
    CONSTRAINT chk_tipo_pago CHECK (tipo IN ('TARJETA', 'PSE', 'TRANSFERENCIA', 'EFECTIVO', 'ACH')),
    CONSTRAINT chk_tipo_cuenta CHECK (tipo_cuenta IN ('AHORROS', 'CORRIENTE', 'EMPRESARIAL'))
);

-- ========================================
-- TABLA DE HISTORIALES DE ESTADO
-- ========================================

-- Tabla para rastrear cambios de estado de payouts
CREATE TABLE IF NOT EXISTS payout_status_history (
    id SERIAL PRIMARY KEY,
    payout_id VARCHAR(255) NOT NULL,
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20) NOT NULL,
    motivo TEXT,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    FOREIGN KEY (payout_id) REFERENCES payouts(id) ON DELETE CASCADE
);

-- ========================================
-- TABLA DE COMISIONES Y TARIFAS
-- ========================================

-- Tabla para configurar estructuras de comisiones
CREATE TABLE IF NOT EXISTS commission_rates (
    id SERIAL PRIMARY KEY,
    partner_id VARCHAR(255),
    brand_id VARCHAR(255),
    event_type VARCHAR(100),
    commission_type VARCHAR(20) DEFAULT 'PERCENTAGE', -- PERCENTAGE, FIXED, TIERED
    rate_value DECIMAL(10,4) NOT NULL,
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_commission_type CHECK (commission_type IN ('PERCENTAGE', 'FIXED', 'TIERED')),
    CONSTRAINT chk_rate_positive CHECK (rate_value >= 0),
    CONSTRAINT chk_amounts CHECK (min_amount IS NULL OR max_amount IS NULL OR min_amount <= max_amount)
);

-- ========================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

-- Índices para payouts
CREATE INDEX IF NOT EXISTS idx_payouts_partner_id ON payouts(partner_id);
CREATE INDEX IF NOT EXISTS idx_payouts_cycle_id ON payouts(cycle_id);
CREATE INDEX IF NOT EXISTS idx_payouts_estado ON payouts(estado);
CREATE INDEX IF NOT EXISTS idx_payouts_fecha_creacion ON payouts(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_payouts_confirmation_id ON payouts(confirmation_id) WHERE confirmation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_payouts_partner_estado ON payouts(partner_id, estado);
CREATE INDEX IF NOT EXISTS idx_payouts_fecha_estado ON payouts(fecha_creacion, estado);

-- Índices para transactions
CREATE INDEX IF NOT EXISTS idx_transactions_partner_id ON transactions(partner_id);
CREATE INDEX IF NOT EXISTS idx_transactions_payout_id ON transactions(payout_id);
CREATE INDEX IF NOT EXISTS idx_transactions_event_type ON transactions(event_type);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);

-- Índices para payment_methods
CREATE INDEX IF NOT EXISTS idx_payment_methods_payout ON payment_methods(payout_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_tipo ON payment_methods(tipo);
CREATE INDEX IF NOT EXISTS idx_payment_methods_activo ON payment_methods(es_activo) WHERE es_activo = TRUE;

-- Índices para historial
CREATE INDEX IF NOT EXISTS idx_status_history_payout ON payout_status_history(payout_id);
CREATE INDEX IF NOT EXISTS idx_status_history_fecha ON payout_status_history(changed_at);

-- Índices para comisiones
CREATE INDEX IF NOT EXISTS idx_commission_partner ON commission_rates(partner_id) WHERE partner_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_commission_event ON commission_rates(event_type);
CREATE INDEX IF NOT EXISTS idx_commission_active ON commission_rates(is_active) WHERE is_active = TRUE;

-- ========================================
-- VISTAS MATERIALIZADAS PARA REPORTES
-- ========================================

-- Vista para estadísticas de payouts por partner
CREATE MATERIALIZED VIEW IF NOT EXISTS payout_stats_by_partner AS
SELECT 
    partner_id,
    estado,
    COUNT(*) as total_payouts,
    SUM(monto_total) as monto_total,
    AVG(monto_total) as monto_promedio,
    MIN(fecha_creacion) as primer_payout,
    MAX(fecha_creacion) as ultimo_payout,
    COUNT(CASE WHEN estado = 'EXITOSO' THEN 1 END) as payouts_exitosos,
    COUNT(CASE WHEN estado = 'FALLIDO' THEN 1 END) as payouts_fallidos
FROM payouts 
GROUP BY partner_id, estado;

CREATE INDEX IF NOT EXISTS idx_payout_stats_partner ON payout_stats_by_partner(partner_id);

-- Vista para estadísticas diarias
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_payout_stats AS
SELECT 
    DATE(fecha_creacion) as fecha,
    estado,
    moneda,
    COUNT(*) as total_payouts,
    SUM(monto_total) as monto_total,
    AVG(monto_total) as monto_promedio
FROM payouts 
WHERE fecha_creacion >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(fecha_creacion), estado, moneda;

CREATE INDEX IF NOT EXISTS idx_daily_stats_fecha ON daily_payout_stats(fecha);

-- ========================================
-- FUNCIONES DE NEGOCIO
-- ========================================

-- Función para calcular comisión
CREATE OR REPLACE FUNCTION calcular_comision(
    p_partner_id VARCHAR(255),
    p_event_type VARCHAR(100),
    p_amount DECIMAL(15,2)
)
RETURNS DECIMAL(15,2) AS $$
DECLARE
    v_rate DECIMAL(10,4);
    v_commission DECIMAL(15,2);
BEGIN
    -- Buscar tasa de comisión activa
    SELECT rate_value INTO v_rate
    FROM commission_rates 
    WHERE (partner_id = p_partner_id OR partner_id IS NULL)
      AND event_type = p_event_type
      AND is_active = TRUE
      AND (min_amount IS NULL OR p_amount >= min_amount)
      AND (max_amount IS NULL OR p_amount <= max_amount)
      AND CURRENT_TIMESTAMP BETWEEN effective_from AND COALESCE(effective_to, '2099-12-31')
    ORDER BY partner_id NULLS LAST, effective_from DESC
    LIMIT 1;
    
    IF v_rate IS NOT NULL THEN
        v_commission := p_amount * v_rate;
    ELSE
        v_commission := 0;
    END IF;
    
    RETURN v_commission;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar estado de payout
CREATE OR REPLACE FUNCTION actualizar_estado_payout(
    p_payout_id VARCHAR(255),
    p_nuevo_estado VARCHAR(20),
    p_motivo TEXT DEFAULT NULL,
    p_changed_by VARCHAR(255) DEFAULT 'SYSTEM'
)
RETURNS VOID AS $$
DECLARE
    v_estado_anterior VARCHAR(20);
BEGIN
    -- Obtener estado anterior
    SELECT estado INTO v_estado_anterior FROM payouts WHERE id = p_payout_id;
    
    IF v_estado_anterior IS NULL THEN
        RAISE EXCEPTION 'Payout no encontrado: %', p_payout_id;
    END IF;
    
    -- Actualizar estado
    UPDATE payouts 
    SET 
        estado = p_nuevo_estado,
        updated_at = CURRENT_TIMESTAMP,
        fecha_procesamiento = CASE WHEN p_nuevo_estado = 'EN_PROCESO' THEN CURRENT_TIMESTAMP ELSE fecha_procesamiento END,
        fecha_completado = CASE WHEN p_nuevo_estado IN ('EXITOSO', 'FALLIDO') THEN CURRENT_TIMESTAMP ELSE fecha_completado END
    WHERE id = p_payout_id;
    
    -- Registrar en historial
    INSERT INTO payout_status_history (payout_id, estado_anterior, estado_nuevo, motivo, changed_by)
    VALUES (p_payout_id, v_estado_anterior, p_nuevo_estado, p_motivo, p_changed_by);
    
    -- Refrescar vistas materializadas
    REFRESH MATERIALIZED VIEW CONCURRENTLY payout_stats_by_partner;
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_payout_stats;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- TRIGGERS
-- ========================================

-- Trigger para actualizar updated_at en payouts
CREATE OR REPLACE FUNCTION update_payout_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_payout_updated_at
    BEFORE UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION update_payout_timestamp();

-- Trigger para calcular net_amount automáticamente
CREATE OR REPLACE FUNCTION calcular_net_amount()
RETURNS TRIGGER AS $$
BEGIN
    NEW.net_amount = NEW.monto_total - COALESCE(NEW.fee_amount, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calcular_net_amount
    BEFORE INSERT OR UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION calcular_net_amount();

-- ========================================
-- DATOS INICIALES
-- ========================================

-- Insertar tarifas de comisión por defecto
INSERT INTO commission_rates (partner_id, event_type, commission_type, rate_value, currency) VALUES
(NULL, 'VENTA', 'PERCENTAGE', 0.05, 'USD'),
(NULL, 'CONVERSION', 'PERCENTAGE', 0.03, 'USD'),
(NULL, 'CLICK', 'FIXED', 0.10, 'USD'),
(NULL, 'IMPRESION', 'FIXED', 0.01, 'USD')
ON CONFLICT DO NOTHING;

-- Insertar algunos payouts de prueba
INSERT INTO payouts (id, partner_id, cycle_id, monto_total, moneda, estado) VALUES
('payout-001', 'PARTNER001', 'CYCLE-2023-12', 1500.00, 'USD', 'PENDIENTE'),
('payout-002', 'PARTNER002', 'CYCLE-2023-12', 2300.50, 'USD', 'EXITOSO'),
('payout-003', 'PARTNER001', 'CYCLE-2023-11', 890.75, 'USD', 'PROCESANDO')
ON CONFLICT (id) DO NOTHING;

-- Insertar transacciones de ejemplo
INSERT INTO transactions (id, partner_id, payout_id, comision_valor, comision_moneda, event_type) VALUES
('tx-001', 'PARTNER001', 'payout-001', 75.00, 'USD', 'VENTA'),
('tx-002', 'PARTNER001', 'payout-001', 45.00, 'USD', 'CONVERSION'),
('tx-003', 'PARTNER002', 'payout-002', 115.00, 'USD', 'VENTA')
ON CONFLICT (id) DO NOTHING;

-- ========================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ========================================

COMMENT ON TABLE payouts IS 'Tabla principal para gestionar pagos (payouts) a partners';
COMMENT ON COLUMN payouts.estado IS 'Estados: PENDIENTE, CALCULADO, CONFIRMADO, RECHAZADO, EN_PROCESO, EXITOSO, FALLIDO';
COMMENT ON COLUMN payouts.monto_total IS 'Monto total del payout antes de comisiones';
COMMENT ON COLUMN payouts.net_amount IS 'Monto neto después de descontar fees';

COMMENT ON TABLE transactions IS 'Transacciones individuales que componen un payout';
COMMENT ON TABLE payment_methods IS 'Información detallada de métodos de pago por payout';
COMMENT ON TABLE payout_status_history IS 'Historial de cambios de estado de payouts';
COMMENT ON TABLE commission_rates IS 'Configuración de tasas de comisión por partner y tipo de evento';

-- Mensaje de finalización
SELECT 'Pagos Microservice Database Schema creado exitosamente' AS status;