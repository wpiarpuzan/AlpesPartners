#!/usr/bin/env sh
set -eu

echo "[ENTRYPOINT] Iniciando entrypoint"

# Wait for Postgres to be resolvable and accepting connections before starting Flask
echo "[ENTRYPOINT] Esperando a que postgres:5432 esté disponible..."
J=1
while [ $J -le 30 ]; do
    if nc -z postgres 5432 >/dev/null 2>&1; then
        echo "[ENTRYPOINT] postgres:5432 está disponible"
        break
    fi
    echo "[ENTRYPOINT] Esperando postgres:5432... ($J)"
    sleep 2
    J=$((J + 1))
done

if ! nc -z postgres 5432 >/dev/null 2>&1; then
    echo "[ENTRYPOINT] ERROR: postgres:5432 no está disponible tras 60s, abortando."
    exit 1
fi

# If consumers are requested, wait for broker and start them in background before launching the app
if [ "${START_CONSUMERS:-0}" = "1" ]; then
    echo "[ENTRYPOINT] START_CONSUMERS=1, esperando broker:6650 para lanzar consumers"
    k=1
    while [ $k -le 30 ]; do
        if nc -z broker 6650 >/dev/null 2>&1; then
            echo "[ENTRYPOINT] broker:6650 está disponible, lanzando consumers"
            break
        fi
        echo "[ENTRYPOINT] Esperando broker:6650... ($k)"
        sleep 2
        k=$((k + 1))
    done

    if ! nc -z broker 6650 >/dev/null 2>&1; then
        echo "[ENTRYPOINT] ERROR: broker:6650 no está disponible tras 60s. No se lanzarán los consumers."
    else
        echo "[ENTRYPOINT] Lanzando consumers en background"
        python -m pagos.infrastructure.saga_consumer &
        python -m campanias.infrastructure.consumidores &
        python -m cliente.infrastructure.saga_consumer &
        echo "[ENTRYPOINT] Consumers lanzados"
    fi
else
    echo "[ENTRYPOINT] START_CONSUMERS!=1, omitiendo lanzamiento de consumers"
fi

echo "[ENTRYPOINT] Ejecutando Flask en foreground (PID 1)"
# Use exec so the flask process replaces this shell and its stdout/stderr are visible in container logs
exec flask --app alpespartners.api:create_app run --host=0.0.0.0 --port=5000 --no-reload
