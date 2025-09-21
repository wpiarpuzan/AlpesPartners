-- ========================================
-- ALPESPARTNERS CORE DATABASE SCHEMA
-- ========================================
-- Base de datos principal para el servicio core de Alpes Partners
-- Incluye tablas técnicas compartidas y configuración global

-- Configuración inicial
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABLAS TÉCNICAS (EVENT SOURCING)
-- ========================================

-- Tabla para almacenar eventos del Event Store
CREATE TABLE IF NOT EXISTS event_store (
    id SERIAL PRIMARY KEY,
    aggregate_id VARCHAR(255) NOT NULL,
    aggregate_type VARCHAR(255),
    type VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    occurred_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para event_store
CREATE INDEX IF NOT EXISTS idx_event_store_aggregate_id ON event_store(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_event_store_type ON event_store(type);
CREATE INDEX IF NOT EXISTS idx_event_store_occurred_on ON event_store(occurred_on);

-- ========================================
-- PATRÓN OUTBOX PARA EVENTOS DE INTEGRACIÓN
-- ========================================

-- Tabla Outbox para garantizar entrega de eventos
CREATE TABLE IF NOT EXISTS outbox (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

-- Índices para outbox
CREATE INDEX IF NOT EXISTS idx_outbox_status ON outbox(status);
CREATE INDEX IF NOT EXISTS idx_outbox_created_at ON outbox(created_at);
CREATE INDEX IF NOT EXISTS idx_outbox_event_type ON outbox(event_type);

-- ========================================
-- DEDUPLICACIÓN DE EVENTOS
-- ========================================

-- Tabla para evitar procesamiento duplicado de eventos
CREATE TABLE IF NOT EXISTS processed_events (
    id SERIAL PRIMARY KEY,
    aggregate_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(aggregate_id, event_type, event_id)
);

-- Índices para processed_events
CREATE INDEX IF NOT EXISTS idx_processed_events_aggregate ON processed_events(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_processed_events_type ON processed_events(event_type);

-- ========================================
-- CONFIGURACIÓN GLOBAL DEL SISTEMA
-- ========================================

-- Tabla de configuración del sistema
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuraciones iniciales
INSERT INTO system_config (config_key, config_value, description) VALUES
('system.version', '1.0.0', 'Versión actual del sistema AlpesPartners'),
('event_store.enabled', 'true', 'Event Sourcing habilitado'),
('outbox.enabled', 'true', 'Patrón Outbox habilitado'),
('pulsar.retry_attempts', '5', 'Número de reintentos para Pulsar')
ON CONFLICT (config_key) DO NOTHING;

-- ========================================
-- TABLAS DE AUDITORÍA
-- ========================================

-- Tabla de auditoría para cambios críticos
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Índices para audit_log
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_by ON audit_log(changed_by);

-- ========================================
-- VISTAS Y FUNCIONES AUXILIARES
-- ========================================

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ========================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ========================================

COMMENT ON TABLE event_store IS 'Almacén de eventos para Event Sourcing de todos los agregados';
COMMENT ON TABLE outbox IS 'Patrón Outbox para garantizar entrega de eventos de integración';
COMMENT ON TABLE processed_events IS 'Registro de eventos procesados para evitar duplicación';
COMMENT ON TABLE system_config IS 'Configuración global del sistema AlpesPartners';
COMMENT ON TABLE audit_log IS 'Registro de auditoría para operaciones críticas';

-- Mensaje de finalización
SELECT 'AlpesPartners Core Database Schema creado exitosamente' AS status;