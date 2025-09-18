#!/usr/bin/env bash
set -euo pipefail

echo "[E2E] Bajando todos los servicios y eliminando volúmenes..."
docker compose down -v
