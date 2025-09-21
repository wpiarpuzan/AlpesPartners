#!/usr/bin/env sh
set -eu

echo "[ENTRYPOINT] Iniciando entrypoint"

## Resolve DB host from DB_URL or DATABASE_URL and wait for it
DB_URL_TO_CHECK="${DATABASE_URL:-${DB_URL:-}}"
if [ -n "$DB_URL_TO_CHECK" ]; then
    # extract hostname and port via python to avoid brittle shell parsing
    HOST_PORT=$(python - <<PY
from urllib.parse import urlparse
import os
u=os.getenv('DB_URL') or os.getenv('DATABASE_URL') or ''
if not u:
    print('')
else:
    p=urlparse(u)
    h=p.hostname or ''
    port = p.port or 5432
    print(f"{h}:{port}")
PY
)
    if [ -n "$HOST_PORT" ]; then
        HOST=$(echo "$HOST_PORT" | cut -d: -f1)
        DB_PORT=$(echo "$HOST_PORT" | cut -d: -f2)
        echo "[ENTRYPOINT] Esperando a que la DB $HOST:$DB_PORT esté disponible..."
        J=1
        while [ $J -le 60 ]; do
            if nc -z "$HOST" "$DB_PORT" >/dev/null 2>&1; then
                echo "[ENTRYPOINT] $HOST:$DB_PORT está disponible"
                break
            fi
            echo "[ENTRYPOINT] Esperando $HOST:$DB_PORT... ($J)"
            sleep 2
            J=$((J + 1))
        done
        if ! nc -z "$HOST" "$DB_PORT" >/dev/null 2>&1; then
            echo "[ENTRYPOINT] ERROR: $HOST:$DB_PORT no está disponible tras timeout, abortando."
            exit 1
        fi
        # Run migrations (if any)
        echo "[ENTRYPOINT] Ejecutando migraciones SQL (si existen)"
        python -m alpespartners.scripts.run_migrations || {
            echo "[ENTRYPOINT] ERROR: fallaron las migraciones"
            exit 1
        }
    else
        echo "[ENTRYPOINT] No se pudo parsear DB_URL/DATABASE_URL; omitiendo espera de DB"
    fi
else
    echo "[ENTRYPOINT] No se proporcionó DB_URL o DATABASE_URL; se usará el comportamiento previo (espera a 'postgres')"
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
# Determine port: prefer PORT (used by some services), then BFF_PORT, default 5000
FLASK_PORT="${PORT:-${BFF_PORT:-5000}}"
echo "[ENTRYPOINT] Starting Flask on port $FLASK_PORT"
# Use exec so the flask process replaces this shell and its stdout/stderr are visible in container logs
exec flask --app alpespartners.api:create_app run --host=0.0.0.0 --port="$FLASK_PORT" --no-reload
