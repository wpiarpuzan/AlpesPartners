#!/bin/bash
set -e

CAMPANIA_ID="camp-e2e-003"

# Crear campaña
curl -s -X POST http://localhost:5000/campanias/comandos/crear \
  -H "Content-Type: application/json" \
  -d '{"idCampania": "'$CAMPANIA_ID'", "idCliente": "cli3", "itinerario": []}'
echo "[E2E] Campaña creada: $CAMPANIA_ID"

# Simular pago confirmado dos veces
EVENTO_JSON='{"type":"PagoConfirmado.v1","data":{"idCampania":"'"$CAMPANIA_ID"'"}}'
TMPFILE=$(mktemp)
echo "$EVENTO_JSON" > "$TMPFILE"
chmod 0644 "$TMPFILE"
docker cp "$TMPFILE" broker:/tmp/evento.json
rm "$TMPFILE"
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos"
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos"
echo "[E2E] Pago confirmado enviado dos veces."

# Verificar processed_events (no debe haber duplicados)
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos-json"
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos-json"
echo "[E2E] Pago confirmado enviado dos veces."

# Query processed_events in the correct DB
docker exec -i postgres psql -U admin -d alpespartner -c "select aggregate_id,event_type,count(*) from processed_events where aggregate_id='$CAMPANIA_ID' group by 1,2;"
