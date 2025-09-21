-- V2__add_id_cliente.sql
-- Add id_cliente column to campanias_view to match application inserts

ALTER TABLE IF EXISTS campanias_view
ADD COLUMN IF NOT EXISTS id_cliente TEXT;
