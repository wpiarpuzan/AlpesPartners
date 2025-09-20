-- ========================================
-- CLIENTE MICROSERVICE DATABASE SCHEMA
-- ========================================
-- Base de datos para el microservicio de Clientes
-- Gestiona información de clientes naturales y empresariales

-- Configuración inicial
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABLA PRINCIPAL DE CLIENTES
-- ========================================

-- Tabla principal para almacenar clientes (naturales y empresariales)
CREATE TABLE IF NOT EXISTS clientes (
    id VARCHAR(255) PRIMARY KEY,
    nombre VARCHAR(500) NOT NULL,
    email VARCHAR(255),
    cedula VARCHAR(50),
    rut VARCHAR(50),
    fecha_nacimiento TIMESTAMP,
    fecha_constitucion TIMESTAMP,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_pagos INTEGER DEFAULT 0,
    ultimo_pago TIMESTAMP,
    monto_total_pagos DECIMAL(15,2) DEFAULT 0.00,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    tipo_cliente VARCHAR(20) DEFAULT 'NATURAL', -- NATURAL, EMPRESA
    telefono VARCHAR(20),
    direccion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(100) DEFAULT 'Colombia',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_tipo_cliente CHECK (tipo_cliente IN ('NATURAL', 'EMPRESA')),
    CONSTRAINT chk_estado_cliente CHECK (estado IN ('ACTIVO', 'INACTIVO', 'SUSPENDIDO')),
    CONSTRAINT chk_total_pagos CHECK (total_pagos >= 0),
    CONSTRAINT chk_monto_total CHECK (monto_total_pagos >= 0),
    
    -- Para clientes naturales, cedula es obligatoria
    -- Para clientes empresa, RUT es obligatorio
    CONSTRAINT chk_cliente_natural CHECK (
        (tipo_cliente = 'NATURAL' AND cedula IS NOT NULL) OR 
        (tipo_cliente = 'EMPRESA')
    ),
    CONSTRAINT chk_cliente_empresa CHECK (
        (tipo_cliente = 'EMPRESA' AND rut IS NOT NULL) OR 
        (tipo_cliente = 'NATURAL')
    )
);

-- ========================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

-- Índices principales
CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);
CREATE INDEX IF NOT EXISTS idx_clientes_cedula ON clientes(cedula) WHERE cedula IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_clientes_rut ON clientes(rut) WHERE rut IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_clientes_tipo ON clientes(tipo_cliente);
CREATE INDEX IF NOT EXISTS idx_clientes_estado ON clientes(estado);
CREATE INDEX IF NOT EXISTS idx_clientes_fecha_registro ON clientes(fecha_registro);
CREATE INDEX IF NOT EXISTS idx_clientes_ultimo_pago ON clientes(ultimo_pago);
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);
CREATE INDEX IF NOT EXISTS idx_clientes_ciudad ON clientes(ciudad);

-- Índice compuesto para búsquedas
CREATE INDEX IF NOT EXISTS idx_clientes_busqueda ON clientes(estado, tipo_cliente, fecha_registro);

-- ========================================
-- TABLA DE DIRECCIONES (OPCIONAL - EXPANSIÓN FUTURA)
-- ========================================

CREATE TABLE IF NOT EXISTS cliente_direcciones (
    id SERIAL PRIMARY KEY,
    cliente_id VARCHAR(255) NOT NULL,
    tipo_direccion VARCHAR(50) DEFAULT 'PRINCIPAL', -- PRINCIPAL, FACTURACION, ENVIO
    direccion_completa TEXT NOT NULL,
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    codigo_postal VARCHAR(20),
    pais VARCHAR(100) DEFAULT 'Colombia',
    es_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    CONSTRAINT chk_tipo_direccion CHECK (tipo_direccion IN ('PRINCIPAL', 'FACTURACION', 'ENVIO'))
);

-- Índices para direcciones
CREATE INDEX IF NOT EXISTS idx_direcciones_cliente ON cliente_direcciones(cliente_id);
CREATE INDEX IF NOT EXISTS idx_direcciones_principal ON cliente_direcciones(es_principal) WHERE es_principal = TRUE;

-- ========================================
-- TABLA DE CONTACTOS ADICIONALES
-- ========================================

CREATE TABLE IF NOT EXISTS cliente_contactos (
    id SERIAL PRIMARY KEY,
    cliente_id VARCHAR(255) NOT NULL,
    tipo_contacto VARCHAR(50) NOT NULL, -- TELEFONO, WHATSAPP, EMAIL_SECUNDARIO
    valor_contacto VARCHAR(255) NOT NULL,
    es_principal BOOLEAN DEFAULT FALSE,
    es_verificado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    CONSTRAINT chk_tipo_contacto CHECK (tipo_contacto IN ('TELEFONO', 'WHATSAPP', 'EMAIL_SECUNDARIO', 'FAX'))
);

-- Índices para contactos
CREATE INDEX IF NOT EXISTS idx_contactos_cliente ON cliente_contactos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_contactos_tipo ON cliente_contactos(tipo_contacto);

-- ========================================
-- TABLA DE PREFERENCIAS DEL CLIENTE
-- ========================================

CREATE TABLE IF NOT EXISTS cliente_preferencias (
    id SERIAL PRIMARY KEY,
    cliente_id VARCHAR(255) NOT NULL,
    notificaciones_email BOOLEAN DEFAULT TRUE,
    notificaciones_sms BOOLEAN DEFAULT FALSE,
    newsletter BOOLEAN DEFAULT TRUE,
    ofertas_especiales BOOLEAN DEFAULT TRUE,
    idioma_preferido VARCHAR(10) DEFAULT 'es',
    zona_horaria VARCHAR(50) DEFAULT 'America/Bogota',
    moneda_preferida VARCHAR(3) DEFAULT 'COP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    UNIQUE(cliente_id)
);

-- ========================================
-- VISTAS MATERIALIZADAS PARA REPORTES
-- ========================================

-- Vista para estadísticas de clientes
CREATE MATERIALIZED VIEW IF NOT EXISTS clientes_estadisticas AS
SELECT 
    tipo_cliente,
    estado,
    COUNT(*) as total_clientes,
    AVG(total_pagos) as promedio_pagos,
    SUM(monto_total_pagos) as monto_total,
    MIN(fecha_registro) as primer_registro,
    MAX(fecha_registro) as ultimo_registro
FROM clientes 
GROUP BY tipo_cliente, estado;

-- Índice para la vista materializada
CREATE INDEX IF NOT EXISTS idx_clientes_stats_tipo_estado ON clientes_estadisticas(tipo_cliente, estado);

-- ========================================
-- FUNCIONES DE NEGOCIO
-- ========================================

-- Función para actualizar estadísticas de pago
CREATE OR REPLACE FUNCTION actualizar_estadisticas_cliente(
    p_cliente_id VARCHAR(255),
    p_monto_pago DECIMAL(15,2),
    p_fecha_pago TIMESTAMP
)
RETURNS VOID AS $$
BEGIN
    UPDATE clientes 
    SET 
        total_pagos = COALESCE(total_pagos, 0) + 1,
        monto_total_pagos = COALESCE(monto_total_pagos, 0) + p_monto_pago,
        ultimo_pago = p_fecha_pago,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_cliente_id;
    
    -- Refrescar vista materializada
    REFRESH MATERIALIZED VIEW CONCURRENTLY clientes_estadisticas;
END;
$$ LANGUAGE plpgsql;

-- Función para validar email
CREATE OR REPLACE FUNCTION validar_email(email_input TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email_input ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- TRIGGERS
-- ========================================

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_cliente_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cliente_updated_at
    BEFORE UPDATE ON clientes
    FOR EACH ROW
    EXECUTE FUNCTION update_cliente_timestamp();

-- Trigger para validar email
CREATE OR REPLACE FUNCTION validar_cliente_email()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email IS NOT NULL AND NOT validar_email(NEW.email) THEN
        RAISE EXCEPTION 'Email inválido: %', NEW.email;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_email
    BEFORE INSERT OR UPDATE ON clientes
    FOR EACH ROW
    EXECUTE FUNCTION validar_cliente_email();

-- ========================================
-- DATOS INICIALES DE PRUEBA
-- ========================================

-- Insertar algunos clientes de prueba
INSERT INTO clientes (id, nombre, email, cedula, tipo_cliente, ciudad, estado) VALUES
('cliente-001', 'Juan Carlos Pérez', 'juan.perez@email.com', '12345678', 'NATURAL', 'Bogotá', 'ACTIVO'),
('cliente-002', 'María Elena García', 'maria.garcia@email.com', '87654321', 'NATURAL', 'Medellín', 'ACTIVO'),
('cliente-003', 'Empresa ABC S.A.S.', 'contacto@empresaabc.com', NULL, 'EMPRESA', 'Cali', 'ACTIVO')
ON CONFLICT (id) DO NOTHING;

-- Actualizar RUT para la empresa
UPDATE clientes SET rut = '900123456-1' WHERE id = 'cliente-003';

-- Insertar preferencias para clientes de prueba
INSERT INTO cliente_preferencias (cliente_id) 
SELECT id FROM clientes WHERE id IN ('cliente-001', 'cliente-002', 'cliente-003')
ON CONFLICT (cliente_id) DO NOTHING;

-- ========================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ========================================

COMMENT ON TABLE clientes IS 'Tabla principal para almacenar información de clientes naturales y empresariales';
COMMENT ON COLUMN clientes.tipo_cliente IS 'Tipo de cliente: NATURAL para personas físicas, EMPRESA para personas jurídicas';
COMMENT ON COLUMN clientes.estado IS 'Estado del cliente: ACTIVO, INACTIVO, SUSPENDIDO';
COMMENT ON COLUMN clientes.total_pagos IS 'Número total de pagos realizados por el cliente';
COMMENT ON COLUMN clientes.monto_total_pagos IS 'Suma total de todos los pagos del cliente';

COMMENT ON TABLE cliente_direcciones IS 'Direcciones adicionales de clientes (expansión futura)';
COMMENT ON TABLE cliente_contactos IS 'Información de contacto adicional para clientes';
COMMENT ON TABLE cliente_preferencias IS 'Preferencias de comunicación y configuración del cliente';

COMMENT ON MATERIALIZED VIEW clientes_estadisticas IS 'Vista materializada con estadísticas agregadas de clientes';

-- Mensaje de finalización
SELECT 'Cliente Microservice Database Schema creado exitosamente' AS status;