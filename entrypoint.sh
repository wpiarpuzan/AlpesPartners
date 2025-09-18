# Esperar a que el broker de Pulsar esté disponible
echo "[ENTRYPOINT] Esperando a que broker:6650 esté disponible..."
for i in {1..30}; do
	nc -z broker 6650 && echo "[ENTRYPOINT] broker:6650 está disponible" && break
	echo "[ENTRYPOINT] Esperando broker:6650... ($i)"
	sleep 2
done
if ! nc -z broker 6650; then
	echo "[ENTRYPOINT] ERROR: broker:6650 no está disponible tras 60s, abortando."
	exit 1
fi
#!/bin/bash
# Script robusto para lanzar Flask API y consumers en background
set -e

# Lanzar Flask API en background
flask --app alpespartners.api:create_app run --host=0.0.0.0 --port=5000 --no-reload &
FLASK_PID=$!

echo "[ENTRYPOINT] Flask lanzado con PID $FLASK_PID"

# Lanzar consumers explícitamente solo si START_CONSUMERS=1
PAGOS_PID=""
CAMPANIAS_PID=""
CLIENTE_PID=""
if [ "${START_CONSUMERS:-0}" = "1" ]; then
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

# Esperar a que Flask termine (mantiene el contenedor vivo)
wait $FLASK_PID
