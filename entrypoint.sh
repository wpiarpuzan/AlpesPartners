#!/usr/bin/env sh
set -eu
#!/usr/bin/env sh
set -eu

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

echo "[ENTRYPOINT] Starting Flask API"
flask --app alpespartners.api:create_app run --host=0.0.0.0 --port=5000 --no-reload &
FLASK_PID=$!
echo "[ENTRYPOINT] Flask lanzado con PID $FLASK_PID"

# Optionally start consumers only when START_CONSUMERS=1
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
        python -m pagos.infrastructure.saga_consumer &
        PAGOS_PID=$!
        python -m campanias.infrastructure.consumidores &
        CAMPANIAS_PID=$!
        python -m cliente.infrastructure.saga_consumer &
        CLIENTE_PID=$!
        echo "[ENTRYPOINT] Consumers lanzados: pagos=$PAGOS_PID campanias=$CAMPANIAS_PID cliente=$CLIENTE_PID"
    fi
else
    echo "[ENTRYPOINT] START_CONSUMERS!=1, omitiendo lanzamiento de consumers"
fi

# Wait to keep container alive
wait "$FLASK_PID"
