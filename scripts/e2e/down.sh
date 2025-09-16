#!/bin/bash
set -e

echo "[E2E] Bajando todos los servicios y eliminando volúmenes..."
docker compose down -v
