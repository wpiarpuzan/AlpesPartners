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
<<<<<<< HEAD
);

-- ========================================
-- TABLA DE CONTENIDO DE CAMPAÑAS
-- ========================================

-- Tabla para almacenar contenido creativo de campañas
CREATE TABLE IF NOT EXISTS campaign_content (
    id SERIAL PRIMARY KEY,
    campania_id VARCHAR(255) NOT NULL,
    tipo_contenido VARCHAR(50) NOT NULL,
    titulo VARCHAR(255),
    descripcion TEXT,
    url_imagen VARCHAR(500),
    url_video VARCHAR(500),
    call_to_action VARCHAR(100),
    landing_page_url VARCHAR(500),
    tracking_url VARCHAR(500),
    formato VARCHAR(50), -- banner, video, texto, carousel
    dimensiones VARCHAR(20), -- 300x250, 728x90, etc
    peso_kb INTEGER,
    duracion_segundos INTEGER, -- Para videos
    idioma VARCHAR(10) DEFAULT 'es',
    es_activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por VARCHAR(255),
    aprobado_por VARCHAR(255),
    fecha_aprobacion TIMESTAMP,
    version INTEGER DEFAULT 1,
    
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_tipo_contenido CHECK (tipo_contenido IN ('BANNER', 'VIDEO', 'TEXTO', 'CAROUSEL', 'INTERACTIVO')),
    CONSTRAINT chk_formato CHECK (formato IN ('banner', 'video', 'texto', 'carousel', 'pop-up', 'native')),
    CONSTRAINT chk_peso_positivo CHECK (peso_kb > 0),
    CONSTRAINT chk_duracion_positiva CHECK (duracion_segundos IS NULL OR duracion_segundos > 0)
);

-- ========================================
-- TABLA DE TRACKING Y MÉTRICAS
-- ========================================

-- Tabla para almacenar eventos de tracking
CREATE TABLE IF NOT EXISTS campaign_tracking (
    id SERIAL PRIMARY KEY,
    campania_id VARCHAR(255) NOT NULL,
    content_id INTEGER,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    timestamp_event TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address INET,
    referrer VARCHAR(500),
    landing_page VARCHAR(500),
    device_type VARCHAR(20),
    os VARCHAR(50),
    browser VARCHAR(50),
    country_code VARCHAR(2),
    city VARCHAR(100),
    conversion_value DECIMAL(15,2),
    revenue DECIMAL(15,2),
    cost DECIMAL(15,2),
    custom_attributes JSONB,
    
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES campaign_content(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_event_type CHECK (event_type IN ('IMPRESSION', 'CLICK', 'VIEW', 'CONVERSION', 'INSTALL', 'PURCHASE', 'LEAD')),
    CONSTRAINT chk_device_type CHECK (device_type IN ('desktop', 'mobile', 'tablet', 'tv', 'other')),
    CONSTRAINT chk_valores_positivos CHECK (
        (conversion_value IS NULL OR conversion_value >= 0) AND
        (revenue IS NULL OR revenue >= 0) AND
        (cost IS NULL OR cost >= 0)
    )
);

-- ========================================
-- TABLA DE MÉTRICAS AGREGADAS
-- ========================================

-- Tabla para almacenar métricas diarias agregadas por campaña
CREATE TABLE IF NOT EXISTS campaign_daily_metrics (
    id SERIAL PRIMARY KEY,
    campania_id VARCHAR(255) NOT NULL,
    fecha DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    installs INTEGER DEFAULT 0,
    purchases INTEGER DEFAULT 0,
    leads INTEGER DEFAULT 0,
    total_revenue DECIMAL(15,2) DEFAULT 0.00,
    total_cost DECIMAL(15,2) DEFAULT 0.00,
    unique_users INTEGER DEFAULT 0,
    ctr DECIMAL(5,4),
    conversion_rate DECIMAL(5,4),
    cpc DECIMAL(8,2),
    cpm DECIMAL(8,2),
    roas DECIMAL(8,2), -- Return on Ad Spend
    roi DECIMAL(8,2),  -- Return on Investment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE,
    
    UNIQUE(campania_id, fecha),
    
    CONSTRAINT chk_metricas_positivas CHECK (
        impressions >= 0 AND clicks >= 0 AND views >= 0 AND 
        conversions >= 0 AND installs >= 0 AND purchases >= 0 AND leads >= 0 AND
        total_revenue >= 0 AND total_cost >= 0 AND unique_users >= 0
    ),
    CONSTRAINT chk_rates_validas_metrics CHECK (
        (ctr IS NULL OR ctr BETWEEN 0 AND 1) AND
        (conversion_rate IS NULL OR conversion_rate BETWEEN 0 AND 1)
    )
);

-- ========================================
-- TABLA DE CONFIGURACIONES DE CAMPAÑA
-- ========================================

-- Tabla para configuraciones específicas de campaña
CREATE TABLE IF NOT EXISTS campaign_configurations (
    id SERIAL PRIMARY KEY,
    campania_id VARCHAR(255) NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    descripcion TEXT,
    es_activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE,
    
    UNIQUE(campania_id, config_key),
    
    CONSTRAINT chk_config_type CHECK (config_type IN ('string', 'number', 'boolean', 'json'))
);

-- ========================================
-- TABLA DE AUDIENCIAS
-- ========================================

-- Tabla para definir audiencias objetivo
CREATE TABLE IF NOT EXISTS campaign_audiences (
    id SERIAL PRIMARY KEY,
    campania_id VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    criterios JSONB NOT NULL, -- Criterios de segmentación
    tamaño_estimado INTEGER,
    edad_min INTEGER,
    edad_max INTEGER,
    generos VARCHAR(50)[], -- array de géneros
    intereses VARCHAR(100)[], -- array de intereses
    comportamientos VARCHAR(100)[], -- array de comportamientos
    ubicaciones VARCHAR(100)[], -- array de ubicaciones
    idiomas VARCHAR(10)[], -- array de idiomas
    dispositivos VARCHAR(20)[], -- array de dispositivos
    es_activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campania_id) REFERENCES campanias(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_edades_validas CHECK (
        (edad_min IS NULL OR edad_min >= 13) AND
        (edad_max IS NULL OR edad_max <= 100) AND
        (edad_min IS NULL OR edad_max IS NULL OR edad_min <= edad_max)
    ),
    CONSTRAINT chk_tamaño_positivo CHECK (tamaño_estimado IS NULL OR tamaño_estimado >= 0)
);

-- ========================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

-- Índices principales para campanias
CREATE INDEX IF NOT EXISTS idx_campanias_partner_id ON campanias(partner_id);
CREATE INDEX IF NOT EXISTS idx_campanias_brand_id ON campanias(brand_id);
CREATE INDEX IF NOT EXISTS idx_campanias_estado ON campanias(estado);
CREATE INDEX IF NOT EXISTS idx_campanias_tipo ON campanias(tipo_campania);
CREATE INDEX IF NOT EXISTS idx_campanias_fechas ON campanias(fecha_inicio, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_campanias_categoria ON campanias(categoria);
CREATE INDEX IF NOT EXISTS idx_campanias_creacion ON campanias(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_campanias_partner_estado ON campanias(partner_id, estado);

-- Índices para contenido
CREATE INDEX IF NOT EXISTS idx_content_campania ON campaign_content(campania_id);
CREATE INDEX IF NOT EXISTS idx_content_tipo ON campaign_content(tipo_contenido);
CREATE INDEX IF NOT EXISTS idx_content_activo ON campaign_content(es_activo) WHERE es_activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_content_formato ON campaign_content(formato);

-- Índices para tracking (críticos para performance)
CREATE INDEX IF NOT EXISTS idx_tracking_campania ON campaign_tracking(campania_id);
CREATE INDEX IF NOT EXISTS idx_tracking_content ON campaign_tracking(content_id);
CREATE INDEX IF NOT EXISTS idx_tracking_event_type ON campaign_tracking(event_type);
CREATE INDEX IF NOT EXISTS idx_tracking_timestamp ON campaign_tracking(timestamp_event);
CREATE INDEX IF NOT EXISTS idx_tracking_user ON campaign_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_tracking_session ON campaign_tracking(session_id);
CREATE INDEX IF NOT EXISTS idx_tracking_device ON campaign_tracking(device_type);
CREATE INDEX IF NOT EXISTS idx_tracking_country ON campaign_tracking(country_code);

-- Índices compuestos para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_tracking_campania_event_time ON campaign_tracking(campania_id, event_type, timestamp_event);
CREATE INDEX IF NOT EXISTS idx_tracking_daily_agg ON campaign_tracking(campania_id, DATE(timestamp_event), event_type);

-- Índices para métricas diarias
CREATE INDEX IF NOT EXISTS idx_daily_metrics_campania ON campaign_daily_metrics(campania_id);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_fecha ON campaign_daily_metrics(fecha);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_campania_fecha ON campaign_daily_metrics(campania_id, fecha);

-- Índices para configuraciones
CREATE INDEX IF NOT EXISTS idx_config_campania ON campaign_configurations(campania_id);
CREATE INDEX IF NOT EXISTS idx_config_key ON campaign_configurations(config_key);
CREATE INDEX IF NOT EXISTS idx_config_activo ON campaign_configurations(es_activo) WHERE es_activo = TRUE;

-- Índices para audiencias
CREATE INDEX IF NOT EXISTS idx_audiences_campania ON campaign_audiences(campania_id);
CREATE INDEX IF NOT EXISTS idx_audiences_activa ON campaign_audiences(es_activa) WHERE es_activa = TRUE;

-- ========================================
-- VISTAS MATERIALIZADAS PARA REPORTES
-- ========================================

-- Vista para estadísticas de campaña
CREATE MATERIALIZED VIEW IF NOT EXISTS campaign_performance_summary AS
SELECT 
    c.id,
    c.nombre,
    c.partner_id,
    c.estado,
    c.presupuesto_total,
    c.presupuesto_utilizado,
    COALESCE(SUM(m.impressions), 0) as total_impressions,
    COALESCE(SUM(m.clicks), 0) as total_clicks,
    COALESCE(SUM(m.conversions), 0) as total_conversions,
    COALESCE(SUM(m.total_revenue), 0) as total_revenue,
    COALESCE(SUM(m.total_cost), 0) as total_cost,
    CASE 
        WHEN SUM(m.impressions) > 0 THEN ROUND(SUM(m.clicks)::DECIMAL / SUM(m.impressions) * 100, 4)
        ELSE 0 
    END as ctr_avg,
    CASE 
        WHEN SUM(m.clicks) > 0 THEN ROUND(SUM(m.conversions)::DECIMAL / SUM(m.clicks) * 100, 4)
        ELSE 0 
    END as conversion_rate_avg,
    CASE 
        WHEN SUM(m.total_cost) > 0 THEN ROUND(SUM(m.total_revenue) / SUM(m.total_cost), 2)
        ELSE 0 
    END as roas_avg,
    COUNT(DISTINCT m.fecha) as dias_activos
FROM campanias c
LEFT JOIN campaign_daily_metrics m ON c.id = m.campania_id
GROUP BY c.id, c.nombre, c.partner_id, c.estado, c.presupuesto_total, c.presupuesto_utilizado;

CREATE INDEX IF NOT EXISTS idx_perf_summary_partner ON campaign_performance_summary(partner_id);
CREATE INDEX IF NOT EXISTS idx_perf_summary_estado ON campaign_performance_summary(estado);

-- Vista para métricas por partner
CREATE MATERIALIZED VIEW IF NOT EXISTS partner_campaign_stats AS
SELECT 
    partner_id,
    COUNT(*) as total_campaigns,
    COUNT(CASE WHEN estado = 'ACTIVA' THEN 1 END) as active_campaigns,
    COUNT(CASE WHEN estado = 'FINALIZADA' THEN 1 END) as completed_campaigns,
    SUM(presupuesto_total) as total_budget,
    SUM(presupuesto_utilizado) as used_budget,
    AVG(presupuesto_total) as avg_budget_per_campaign,
    MIN(fecha_creacion) as first_campaign_date,
    MAX(fecha_creacion) as last_campaign_date
FROM campanias
GROUP BY partner_id;

CREATE INDEX IF NOT EXISTS idx_partner_stats_partner ON partner_campaign_stats(partner_id);

-- ========================================
-- FUNCIONES DE NEGOCIO
-- ========================================

-- Función para calcular métricas diarias
CREATE OR REPLACE FUNCTION agregar_metricas_diarias(p_fecha DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    -- Insertar o actualizar métricas diarias agregadas
    INSERT INTO campaign_daily_metrics (
        campania_id, fecha, impressions, clicks, views, conversions, 
        installs, purchases, leads, total_revenue, total_cost, unique_users
    )
    SELECT 
        campania_id,
        DATE(timestamp_event) as fecha,
        COUNT(CASE WHEN event_type = 'IMPRESSION' THEN 1 END) as impressions,
        COUNT(CASE WHEN event_type = 'CLICK' THEN 1 END) as clicks,
        COUNT(CASE WHEN event_type = 'VIEW' THEN 1 END) as views,
        COUNT(CASE WHEN event_type = 'CONVERSION' THEN 1 END) as conversions,
        COUNT(CASE WHEN event_type = 'INSTALL' THEN 1 END) as installs,
        COUNT(CASE WHEN event_type = 'PURCHASE' THEN 1 END) as purchases,
        COUNT(CASE WHEN event_type = 'LEAD' THEN 1 END) as leads,
        COALESCE(SUM(revenue), 0) as total_revenue,
        COALESCE(SUM(cost), 0) as total_cost,
        COUNT(DISTINCT user_id) as unique_users
    FROM campaign_tracking 
    WHERE DATE(timestamp_event) = p_fecha
    GROUP BY campania_id, DATE(timestamp_event)
    ON CONFLICT (campania_id, fecha) 
    DO UPDATE SET
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        views = EXCLUDED.views,
        conversions = EXCLUDED.conversions,
        installs = EXCLUDED.installs,
        purchases = EXCLUDED.purchases,
        leads = EXCLUDED.leads,
        total_revenue = EXCLUDED.total_revenue,
        total_cost = EXCLUDED.total_cost,
        unique_users = EXCLUDED.unique_users;
    
    -- Calcular métricas derivadas
    UPDATE campaign_daily_metrics 
    SET 
        ctr = CASE WHEN impressions > 0 THEN clicks::DECIMAL / impressions ELSE 0 END,
        conversion_rate = CASE WHEN clicks > 0 THEN conversions::DECIMAL / clicks ELSE 0 END,
        cpc = CASE WHEN clicks > 0 THEN total_cost / clicks ELSE 0 END,
        cpm = CASE WHEN impressions > 0 THEN total_cost / impressions * 1000 ELSE 0 END,
        roas = CASE WHEN total_cost > 0 THEN total_revenue / total_cost ELSE 0 END,
        roi = CASE WHEN total_cost > 0 THEN (total_revenue - total_cost) / total_cost * 100 ELSE 0 END
    WHERE fecha = p_fecha;
    
    -- Refrescar vistas materializadas
    REFRESH MATERIALIZED VIEW CONCURRENTLY campaign_performance_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY partner_campaign_stats;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener métricas de campaña
CREATE OR REPLACE FUNCTION obtener_metricas_campania(
    p_campania_id VARCHAR(255),
    p_fecha_inicio DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    p_fecha_fin DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    fecha DATE,
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    revenue DECIMAL(15,2),
    cost DECIMAL(15,2),
    ctr DECIMAL(5,4),
    conversion_rate DECIMAL(5,4),
    roas DECIMAL(8,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.fecha,
        m.impressions,
        m.clicks,
        m.conversions,
        m.total_revenue,
        m.total_cost,
        m.ctr,
        m.conversion_rate,
        m.roas
    FROM campaign_daily_metrics m
    WHERE m.campania_id = p_campania_id
      AND m.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    ORDER BY m.fecha;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- VISTA / TABLA PROYECTADA campanias_view
-- (Required by microservice consumers and tests)
-- ========================================
CREATE TABLE IF NOT EXISTS campanias_view (
    id varchar(255) PRIMARY KEY,
    id_cliente varchar(255),
    estado varchar(64),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ========================================
-- TRIGGERS
-- ========================================

-- Trigger para actualizar fecha de actualización
CREATE OR REPLACE FUNCTION update_campania_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_campania_updated_at
    BEFORE UPDATE ON campanias
    FOR EACH ROW
    EXECUTE FUNCTION update_campania_timestamp();

-- Trigger para actualizar presupuesto utilizado
CREATE OR REPLACE FUNCTION update_presupuesto_utilizado()
RETURNS TRIGGER AS $$
DECLARE
    total_cost DECIMAL(15,2);
BEGIN
    -- Calcular costo total de la campaña
    SELECT COALESCE(SUM(total_cost), 0) INTO total_cost
    FROM campaign_daily_metrics 
    WHERE campania_id = NEW.campania_id;
    
    -- Actualizar presupuesto utilizado
    UPDATE campanias 
    SET presupuesto_utilizado = total_cost
    WHERE id = NEW.campania_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_presupuesto
    AFTER INSERT OR UPDATE ON campaign_daily_metrics
    FOR EACH ROW
    EXECUTE FUNCTION update_presupuesto_utilizado();

-- ========================================
-- DATOS INICIALES
-- ========================================

-- Insertar campañas de ejemplo
INSERT INTO campanias (id, nombre, descripcion, partner_id, tipo_campania, estado, presupuesto_total) VALUES
('camp-001', 'Campaña Black Friday 2023', 'Campaña de conversión para Black Friday', 'PARTNER001', 'CONVERSION', 'ACTIVA', 5000.00),
('camp-002', 'Awareness Primavera', 'Campaña de reconocimiento de marca', 'PARTNER002', 'AWARENESS', 'ACTIVA', 3000.00),
('camp-003', 'Performance Navidad', 'Campaña de performance navideña', 'PARTNER001', 'PERFORMANCE', 'PAUSADA', 8000.00)
ON CONFLICT (id) DO NOTHING;

-- Insertar contenido de ejemplo
INSERT INTO campaign_content (campania_id, tipo_contenido, titulo, formato, dimensiones) VALUES
('camp-001', 'BANNER', 'Black Friday 50% OFF', 'banner', '728x90'),
('camp-001', 'VIDEO', 'Video promocional Black Friday', 'video', '1920x1080'),
('camp-002', 'TEXTO', 'Descubre nuestra nueva colección', 'texto', NULL)
ON CONFLICT DO NOTHING;

-- ========================================
-- JOBS AUTOMÁTICOS
-- ========================================

-- Crear job para agregación diaria (requiere pg_cron extension)
-- SELECT cron.schedule('agregar-metricas-diarias', '0 1 * * *', 'SELECT agregar_metricas_diarias();');

-- ========================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- ========================================

COMMENT ON TABLE campanias IS 'Tabla principal para gestionar campañas de marketing';
COMMENT ON COLUMN campanias.estado IS 'Estados: BORRADOR, ACTIVA, PAUSADA, FINALIZADA, CANCELADA';
COMMENT ON COLUMN campanias.tipo_campania IS 'Tipos: PERFORMANCE, BRANDING, AWARENESS, CONVERSION, RETENTION';
COMMENT ON COLUMN campanias.geolocalizacion IS 'JSON con países y ciudades objetivo';
COMMENT ON COLUMN campanias.dispositivos_objetivo IS 'JSON con tipos de dispositivos: desktop, mobile, tablet';

COMMENT ON TABLE campaign_content IS 'Contenido creativo asociado a campañas';
COMMENT ON TABLE campaign_tracking IS 'Eventos de tracking de campañas en tiempo real';
COMMENT ON TABLE campaign_daily_metrics IS 'Métricas diarias agregadas por campaña';
COMMENT ON TABLE campaign_configurations IS 'Configuraciones específicas por campaña';
COMMENT ON TABLE campaign_audiences IS 'Definición de audiencias objetivo para campañas';

-- Mensaje de finalización
SELECT 'Campanias Microservice Database Schema creado exitosamente' AS status;
=======
);
>>>>>>> bff
