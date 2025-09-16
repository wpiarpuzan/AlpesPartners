#!/usr/bin/env bash
set -euo pipefail

echo "=== E2E DEMO START ==="

echo "[1/5] Levantando servicios..."
./up.sh
sleep 1

echo "[2/5] Happy path (aprobación)..."
./happy_path.sh
sleep 1

echo "[3/5] Compensación (cancelación)..."
./compensacion.sh
sleep 1

echo "[4/5] Idempotencia (duplicados)..."
./idempotencia.sh
sleep 1

echo "[5/5] Outbox check..."
./outbox.sh
sleep 1

echo "[DONE] Bajando y limpiando..."
./down.sh

echo "=== E2E DEMO COMPLETE ==="
