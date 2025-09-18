#!/bin/sh
set -e

echo "Creating databases if not present..."
echo "Checking/creating databases using psql"
exists=$(psql --username "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='alpespartner';")
if [ "x$exists" = 'x1' ]; then
  echo "Database alpespartner already exists"
else
  echo "Creating database alpespartner"
  psql --username "$POSTGRES_USER" -d postgres -c "CREATE DATABASE alpespartner;"
fi

exists=$(psql --username "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='pulsar_manager';")
if [ "x$exists" = 'x1' ]; then
  echo "Database pulsar_manager already exists"
else
  echo "Creating database pulsar_manager"
  psql --username "$POSTGRES_USER" -d postgres -c "CREATE DATABASE pulsar_manager;"
fi

echo "Applying schema to pulsar_manager..."
psql --username "$POSTGRES_USER" -d pulsar_manager -f /docker-entrypoint-initdb.d/pulsar_manager_tables.sql

echo "Applying schema to alpespartner..."
psql --username "$POSTGRES_USER" -d alpespartner -f /docker-entrypoint-initdb.d/alpespartner_tables.sql

echo "Database init script complete."
