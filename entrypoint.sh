#!/usr/bin/env sh
set -eu

echo "[ENTRYPOINT] Esperando a que broker:6650 esté disponible..."
i=1
while [ $i -le 30 ]; do
	if nc -z broker 6650 >/dev/null 2>&1; then
		echo "[ENTRYPOINT] broker:6650 está disponible"
		break
	fi
	echo "[ENTRYPOINT] Esperando broker:6650... ($i)"
	sleep 2
	i=$((i + 1))
done

if ! nc -z broker 6650 >/dev/null 2>&1; then
	echo "[ENTRYPOINT] ERROR: broker:6650 no está disponible tras 60s, abortando."
	exit 1
fi

echo "[ENTRYPOINT] Starting Flask API"
flask --app alpespartners.api:create_app run --host=0.0.0.0 --port=5000 --no-reload &
FLASK_PID=$!
echo "[ENTRYPOINT] Flask lanzado con PID $FLASK_PID"

# Optionally start consumers only when START_CONSUMERS=1
if [ "${START_CONSUMERS:-0}" = "1" ]; then
	echo "[ENTRYPOINT] START_CONSUMERS=1, lanzando consumers"
	python -m pagos.infrastructure.saga_consumer &
	PAGOS_PID=$!
	python -m campanias.infrastructure.consumidores &
	CAMPANIAS_PID=$!
	python -m cliente.infrastructure.saga_consumer &
	CLIENTE_PID=$!
	echo "[ENTRYPOINT] Consumers lanzados: pagos=$PAGOS_PID campanias=$CAMPANIAS_PID cliente=$CLIENTE_PID"
else
	echo "[ENTRYPOINT] START_CONSUMERS!=1, omitiendo lanzamiento de consumers"
fi

# Wait to keep container alive
wait "$FLASK_PID"
