-- V1__init_schema.sql
-- Creates basic tables required by services: processed_events, outbox, event_store, campanias_view

CREATE TABLE IF NOT EXISTS processed_events (
  id SERIAL PRIMARY KEY,
  aggregate_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  event_id TEXT NOT NULL,
  processed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT _uq_processed_event UNIQUE (aggregate_id, event_type, event_id)
);

CREATE TABLE IF NOT EXISTS outbox (
  id SERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT DEFAULT 'PENDING',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  published_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS event_store (
  id SERIAL PRIMARY KEY,
  aggregate_id TEXT NOT NULL,
  aggregate_type TEXT NOT NULL,
  type TEXT NOT NULL,
  payload JSONB,
  occurred_on TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campanias_view (
  id TEXT PRIMARY KEY,
  estado TEXT,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
