#!/usr/bin/env bash
set -euo pipefail

# entrypoint.sh
# - If MESSAGE_BUS=DB_OUTBOX: start the Outbox worker as a background process
# - Otherwise wait for the Pulsar broker at broker:6650
# - Finally exec the container CMD so the web server (gunicorn) runs as PID 1

echo "[ENTRYPOINT] Starting with MESSAGE_BUS=${MESSAGE_BUS:-not-set}"

if [ "${MESSAGE_BUS:-}" = "DB_OUTBOX" ]; then
    echo "[ENTRYPOINT] MESSAGE_BUS=DB_OUTBOX, starting Outbox worker in background"
    # Start the Outbox worker as a separate process so it doesn't block the web server
    # Ensure worker runs with RUN_AS_WORKER=1 so module initializers start pollers
    env RUN_AS_WORKER=1 python -m alpespartners.infra.message_bus.worker &
    WORKER_PID=$!
    echo "[ENTRYPOINT] Outbox worker started with PID $WORKER_PID"
else
    echo "[ENTRYPOINT] Waiting for Pulsar broker at broker:6650 (30 attempts)"
    for i in $(seq 1 30); do
        if nc -z broker 6650; then
            echo "[ENTRYPOINT] broker:6650 is available"
            break
        fi
        echo "[ENTRYPOINT] waiting for broker:6650... ($i)"
        sleep 2
    done
    if ! nc -z broker 6650; then
        echo "[ENTRYPOINT] ERROR: broker:6650 not available after 60s, aborting."
        exit 1
    fi
fi

# Exec the container CMD. Use exec so the CMD receives signals (gunicorn will be PID 1).
echo "[ENTRYPOINT] Execing container CMD: $@"
exec "$@"
	CAMPANIAS_PID=$!
