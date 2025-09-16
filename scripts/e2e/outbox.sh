#!/bin/bash
set -e

# Crear pago (simulación, ajusta según tu API)
# curl -X POST ...

echo "[E2E] Verificando outbox (pagos)..."
docker exec -i postgres psql -U admin -d alpespartner -c "select id,event_type,status from outbox order by id desc limit 10;"
