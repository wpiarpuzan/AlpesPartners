#!/usr/bin/env bash
# Usage: ./allow_null_id_cliente.sh
# Runs ALTER TABLE to allow NULL values in campanias_view.id_cliente inside the running postgres container.
CONTAINER_NAME=postgres
DB_NAME=postgres
DB_USER=admin
# read password from env or fallback
DB_PASS=${POSTGRES_PASSWORD:-admin10100101.}

echo "Running ALTER TABLE to drop NOT NULL on campanias_view.id_cliente in container $CONTAINER_NAME"

docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "ALTER TABLE campanias_view ALTER COLUMN id_cliente DROP NOT NULL;"

echo "Done."
