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