-- Initialize schema in the default database (usually 'postgres')
-- The init script will create the tables used by Pulsar Manager and by
-- the application (processed_events, campanias_view, etc.) in the current
-- database. For cloud environments it's typical to use a managed DB or
-- to run database migrations instead of bundling DB creation in the image.

CREATE TABLE IF NOT EXISTS environments (
  name varchar(256) NOT NULL,
  broker varchar(1024) NOT NULL,
  bookie varchar(1024) NOT NULL,
  token varchar(1024),
  CONSTRAINT PK_name PRIMARY KEY (name),
  UNIQUE (broker)
);

CREATE TABLE IF NOT EXISTS topics_stats (
  topic_stats_id BIGSERIAL PRIMARY KEY,
  environment varchar(255) NOT NULL,
  cluster varchar(255) NOT NULL,
  broker varchar(255) NOT NULL,
  tenant varchar(255) NOT NULL,
  namespace varchar(255) NOT NULL,
  bundle varchar(255) NOT NULL,
  persistent varchar(36) NOT NULL,
  topic varchar(255) NOT NULL,
  producer_count BIGINT,
  subscription_count BIGINT,
  msg_rate_in double precision	,
  msg_throughput_in double precision	,
  msg_rate_out double precision	,
  msg_throughput_out double precision	,
  average_msg_size double precision	,
  storage_size double precision	,
  time_stamp BIGINT
);

CREATE INDEX IF NOT EXISTS ix_topics_stats_timestamp on topics_stats(time_stamp);

CREATE TABLE IF NOT EXISTS publishers_stats (
  publisher_stats_id BIGSERIAL PRIMARY KEY,
  producer_id BIGINT,
  topic_stats_id BIGINT NOT NULL,
  producer_name varchar(255) NOT NULL,
  msg_rate_in double precision	,
  msg_throughput_in double precision	,
  average_msg_size double precision	,
  address varchar(255),
  connected_since varchar(128),
  client_version varchar(36),
  metadata text,
  time_stamp BIGINT,
  CONSTRAINT fk_publishers_stats_topic_stats_id FOREIGN KEY (topic_stats_id) References topics_stats(topic_stats_id)
);

CREATE TABLE IF NOT EXISTS replications_stats (
  replication_stats_id BIGSERIAL PRIMARY KEY,
  topic_stats_id BIGINT NOT NULL,
  cluster varchar(255) NOT NULL,
  connected BOOLEAN,
  msg_rate_in double precision	,
  msg_rate_out double precision	,
  msg_rate_expired double precision	,
  msg_throughput_in double precision	,
  msg_throughput_out double precision	,
  msg_rate_redeliver double precision	,
  replication_backlog BIGINT,
  replication_delay_in_seconds BIGINT,
  inbound_connection varchar(255),
  inbound_connected_since varchar(255),
  outbound_connection varchar(255),
  outbound_connected_since varchar(255),
  time_stamp BIGINT,
  CONSTRAINT FK_replications_stats_topic_stats_id FOREIGN KEY (topic_stats_id) References topics_stats(topic_stats_id)
);

CREATE TABLE IF NOT EXISTS subscriptions_stats (
  subscription_stats_id BIGSERIAL PRIMARY KEY,
  topic_stats_id BIGINT NOT NULL,
  subscription varchar(255) NULL,
  msg_backlog BIGINT,
  msg_rate_expired double precision	,
  msg_rate_out double precision	,
  msg_throughput_out double precision	,
  msg_rate_redeliver double precision	,
  number_of_entries_since_first_not_acked_message BIGINT,
  total_non_contiguous_deleted_messages_range BIGINT,
  subscription_type varchar(16),
  blocked_subscription_on_unacked_msgs BOOLEAN,
  time_stamp BIGINT,
  UNIQUE (topic_stats_id, subscription),
  CONSTRAINT FK_subscriptions_stats_topic_stats_id FOREIGN KEY (topic_stats_id) References topics_stats(topic_stats_id)
);

CREATE TABLE IF NOT EXISTS consumers_stats (
  consumer_stats_id BIGSERIAL PRIMARY KEY,
  consumer varchar(255) NOT NULL,
  topic_stats_id BIGINT NOT NUll,
  replication_stats_id BIGINT,
  subscription_stats_id BIGINT,
  address varchar(255),
  available_permits BIGINT,
  connected_since varchar(255),
  msg_rate_out double precision	,
  msg_throughput_out double precision	,
  msg_rate_redeliver double precision	,
  client_version varchar(36),
  time_stamp BIGINT,
  metadata text
);

CREATE TABLE IF NOT EXISTS tokens (
  token_id BIGSERIAL PRIMARY KEY,
  role varchar(256) NOT NULL,
  description varchar(128),
  token varchar(1024) NOT NUll,
  UNIQUE (role)
);

CREATE TABLE IF NOT EXISTS users (
  user_id BIGSERIAL PRIMARY KEY,
  access_token varchar(256),
  name varchar(256) NOT NULL,
  description varchar(128),
  email varchar(256),
  phone_number varchar(48),
  location varchar(256),
  company varchar(256),
  expire BIGINT NOT NULL,
  password varchar(256),
  UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS tenants (
  tenant_id BIGSERIAL PRIMARY KEY,
  tenant varchar(255) NOT NULL,
  admin_roles varchar(255),
  allowed_clusters varchar(255),
  environment_name varchar(255),
  UNIQUE(tenant)
);

CREATE TABLE IF NOT EXISTS namespaces (
  namespace_id BIGSERIAL PRIMARY KEY,
  tenant varchar(255) NOT NULL,
  namespace varchar(255) NOT NULL,
  UNIQUE(tenant, namespace)
);

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