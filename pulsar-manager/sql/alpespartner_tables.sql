-- Tables for the AlpsPartners application
-- Tabla para marcar eventos procesados (usada por los consumidores para idempotencia)
CREATE TABLE IF NOT EXISTS processed_events (
  id BIGSERIAL PRIMARY KEY,
  aggregate_id varchar(255) NOT NULL,
  event_type varchar(255) NOT NULL,
  event_id varchar(255) NOT NULL,
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT uq_processed_event UNIQUE (aggregate_id, event_type, event_id)
);

-- Tabla proyectada para campanias (vista/proyección actualizada por consumidores)
CREATE TABLE IF NOT EXISTS campanias_view (
  id varchar(255) PRIMARY KEY,
  id_cliente varchar(255),
  estado varchar(64),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
