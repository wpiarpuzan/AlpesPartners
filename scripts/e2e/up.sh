#!/usr/bin/env bash
#set -euo pipefail

echo "[E2E] Levantando servicios (pulsar, bd, alpespartner, e2e)..."
# Include the e2e profile so the newman container is started by this script only
docker compose --profile pulsar --profile bd --profile alpespartner --profile e2e up -d --build

# Esperar health de Pulsar
until curl -sf http://localhost:8080/metrics; do
  echo "[E2E] Esperando Pulsar..."; sleep 3;
done
# Esperar health de Postgres
until docker exec postgres pg_isready -U admin; do
  echo "[E2E] Esperando Postgres..."; sleep 3;
done
# Esperar health de API
until curl -sf http://localhost:5000/health; do
  echo "[E2E] Esperando API..."; sleep 3;
done

echo "[E2E] Todos los servicios están arriba y saludables."
