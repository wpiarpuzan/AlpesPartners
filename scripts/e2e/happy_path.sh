#!/bin/bash
set -e

CAMPANIA_ID="camp-e2e-001"

# Crear campaña
curl -s -X POST http://localhost:5000/campanias/comandos/crear \
  -H "Content-Type: application/json" \
  -d '{"idCampania": "'$CAMPANIA_ID'", "idCliente": "cli1", "itinerario": []}'
echo "[E2E] Campaña creada: $CAMPANIA_ID"

# Consultar proyección (debe ser PENDIENTE)
resp=$(curl -s http://localhost:5000/campanias/$CAMPANIA_ID)
echo "$resp" | grep 'PENDIENTE' || (echo "[E2E] Estado inicial no es PENDIENTE" && exit 1)
echo "[E2E] Proyección inicial OK."

# Simular pago confirmado (produce evento a Pulsar)
EVENTO_JSON='{"type":"PagoConfirmado.v1","data":{"idCampania":"'"$CAMPANIA_ID"'"}}'
# Create a temp file locally, copy into the broker container, then produce from file to avoid any shell-quoting pitfalls
TMPFILE=$(mktemp)
echo "$EVENTO_JSON" > "$TMPFILE"
chmod 0644 "$TMPFILE"
docker cp "$TMPFILE" broker:/tmp/evento.json
rm "$TMPFILE"
echo "[E2E] Waiting up to 10s for consumers to be ready..."
sleep 2
for i in $(seq 1 10); do
  docker logs --tail 200 alpespartner 2>/dev/null | grep -q "Consumers lanzados" && break || sleep 1
done
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos-json"
echo "[E2E] Pago confirmado simulado."

# Reconsultar proyección (debe ser APROBADA)
sleep 2
resp=$(curl -s http://localhost:5000/campanias/$CAMPANIA_ID)
echo "$resp" | grep 'APROBADA' || (echo "[E2E] Estado final no es APROBADA" && exit 1)
echo "[E2E] Proyección final OK."

# Consultas a BD y event_store
docker exec -i postgres psql -U admin -d postgres -c "select * from campanias_view where id='$CAMPANIA_ID';"
docker exec -i postgres psql -U admin -d postgres -c "select id,aggregate_id,type from event_store where aggregate_id='$CAMPANIA_ID' order by id;"
#!/usr/bin/env bash
set -euo pipefail

CAMPANIA_ID="camp-e2e-001"

# Crear campaña
curl -s -X POST http://localhost:5000/campanias/comandos/crear \
  -H "Content-Type: application/json" \
  -d '{"idCampania": "'$CAMPANIA_ID'", "idCliente": "cli1", "itinerario": []}'
echo "[E2E] Campaña creada: $CAMPANIA_ID"

# Consultar proyección (debe ser PENDIENTE)
resp=$(curl -s http://localhost:5000/campanias/$CAMPANIA_ID)
echo "$resp" | grep 'PENDIENTE' || (echo "[E2E] Estado inicial no es PENDIENTE" && exit 1)
echo "[E2E] Proyección inicial OK."

# Simular pago confirmado (produce evento a Pulsar)
EVENTO_JSON='{"type":"PagoConfirmado.v1","data":{"idCampania":"'"$CAMPANIA_ID"'"}}'
# Create a temp file locally, copy into the broker container, then produce from file to avoid any shell-quoting pitfalls
TMPFILE=$(mktemp)
echo "$EVENTO_JSON" > "$TMPFILE"
chmod 0644 "$TMPFILE"
docker cp "$TMPFILE" broker:/tmp/evento.json
rm "$TMPFILE"
echo "[E2E] Waiting up to 10s for consumers to be ready..."
sleep 2
for i in $(seq 1 10); do
  docker logs --tail 200 alpespartner 2>/dev/null | grep -q "Consumers lanzados" && break || sleep 1
done
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos-json"
echo "[E2E] Pago confirmado simulado."

# Reconsultar proyección (debe ser APROBADA)
sleep 2
resp=$(curl -s http://localhost:5000/campanias/$CAMPANIA_ID)
echo "$resp" | grep 'APROBADA' || (echo "[E2E] Estado final no es APROBADA" && exit 1)
echo "[E2E] Proyección final OK."

# Consultas a BD y event_store
docker exec -i postgres psql -U admin -d postgres -c "select * from campanias_view where id='$CAMPANIA_ID';"
docker exec -i postgres psql -U admin -d postgres -c "select id,aggregate_id,type from event_store where aggregate_id='$CAMPANIA_ID' order by id;"

# Métricas
curl -s http://localhost:5000/metrics
