#!/bin/bash
set -e

CAMPANIA_ID="camp-e2e-002"

# Crear campaña
curl -s -X POST http://localhost:5000/campanias/comandos/crear \
  -H "Content-Type: application/json" \
  -d '{"idCampania": "'"$CAMPANIA_ID"'", "idCliente": "cli2", "itinerario": []}'
echo "[E2E] Campaña creada: $CAMPANIA_ID"

# Simular pago revertido (JSON robusto, sin escapes innecesarios)
EVENTO_JSON='{"type":"PagoRevertido.v1","data":{"idCampania":"'"$CAMPANIA_ID"'"}}'
TMPFILE=$(mktemp)
echo "$EVENTO_JSON" > "$TMPFILE"
chmod 0644 "$TMPFILE"
docker cp "$TMPFILE" broker:/tmp/evento.json
rm "$TMPFILE"
docker exec broker /bin/sh -c "bin/pulsar-client produce -f /tmp/evento.json persistent://public/default/eventos-pagos-json"
echo "[E2E] Pago revertido simulado."

# Consultar proyección (debe ser CANCELADA)
sleep 2
resp=$(curl -s http://localhost:5000/campanias/$CAMPANIA_ID)
echo "$resp" | grep 'CANCELADA' || (echo "[E2E] Estado final no es CANCELADA" && exit 1)
echo "[E2E] Proyección cancelada OK."

# Consumir eventos.campanias (temporal)
docker exec broker bin/pulsar-client consume -s e2e-campanias-sub -n 1 persistent://public/default/eventos.campanias