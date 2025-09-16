#!/usr/bin/env bash
# Produce two identical PagoConfirmado events with unique per-run aggregate id and verify idempotency

set -euo pipefail

# Generate unique suffix for this run
SUFFIX=$(date +%s)
CAMPANIA_ID="camp-e2e-${SUFFIX}"
EVENT_ID="evt-${SUFFIX}-1"

# Clean only the rows related to this CAMPANIA_ID to ensure isolated test runs
echo "Cleaning processed_events and event_store rows for aggregate ${CAMPANIA_ID} (if any)"
psql -U admin -h localhost -p 54320 -d postgres -c "DELETE FROM processed_events WHERE aggregate_id='${CAMPANIA_ID}';"
psql -U admin -h localhost -p 54320 -d postgres -c "DELETE FROM event_store WHERE aggregate_id='${CAMPANIA_ID}';"

# Payload with per-run event id
PAYLOAD=$(cat <<JSON
{
  "schemaVersion": "1",
  "aggregateId": "${CAMPANIA_ID}",
  "eventId": "${EVENT_ID}",
  "type": "PagoConfirmado.v1",
  "data": { "estado": "APROBADA", "monto": 123.45 }
}
JSON
)

echo "Producing two identical PagoConfirmado events for campaign ${CAMPANIA_ID} with eventId ${EVENT_ID}"

# Produce twice to test idempotency
pulsar-client produce persistent://public/default/eventos-pagos-json -m "$PAYLOAD"
pulsar-client produce persistent://public/default/eventos-pagos-json -m "$PAYLOAD"

# Wait for consumers to process
sleep 3

echo "Querying processed_events for aggregate ${CAMPANIA_ID}"
psql -U admin -h localhost -p 54320 -d postgres -c "SELECT id, aggregate_id, event_id, created_at FROM processed_events WHERE aggregate_id='${CAMPANIA_ID}' ORDER BY created_at DESC;"

echo "Querying event_store for aggregate ${CAMPANIA_ID}"
psql -U admin -h localhost -p 54320 -d postgres -c "SELECT id, aggregate_id, type, payload->>'eventId' as eventId, created_at FROM event_store WHERE aggregate_id='${CAMPANIA_ID}' ORDER BY created_at DESC;"

