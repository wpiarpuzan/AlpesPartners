#!/usr/bin/env bash
set -euo pipefail

echo "=== E2E SUMMARY ==="
echo "Processed events count:"
docker exec -i postgres psql -U admin -d postgres -c "SELECT count(*) FROM processed_events;"
echo "Outbox recent rows:"
docker exec -i postgres psql -U admin -d postgres -c "SELECT id,event_type,status,created_at FROM outbox ORDER BY id DESC LIMIT 10;"
echo "Recent event_store rows:"
docker exec -i postgres psql -U admin -d postgres -c "SELECT id,aggregate_id,type,occurred_on FROM event_store ORDER BY occurred_on DESC LIMIT 10;"
echo "Campanias view sample:"
docker exec -i postgres psql -U admin -d postgres -c "SELECT id,id_cliente,estado,updated_at FROM campanias_view ORDER BY updated_at DESC LIMIT 10;"
