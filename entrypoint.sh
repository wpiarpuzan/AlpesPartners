#!/bin/bash
# If using DB_OUTBOX mode, skip waiting for broker
if [ "$MESSAGE_BUS" = "DB_OUTBOX" ]; then
	echo "[ENTRYPOINT] MESSAGE_BUS=DB_OUTBOX, skipping broker wait"
else
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
fi
#!/bin/bash
# Script robusto para lanzar Flask API y consumers en background
set -e

# Lanzar Flask API en background
flask --app alpespartners.api:create_app run --host=0.0.0.0 --port=5000 --no-reload &
FLASK_PID=$!

echo "[ENTRYPOINT] Flask lanzado con PID $FLASK_PID"

# Lanzar consumers explícitamente
if [ "$MESSAGE_BUS" = "DB_OUTBOX" ]; then
	echo "[ENTRYPOINT] MESSAGE_BUS=DB_OUTBOX, skipping Pulsar consumers"
else
	# Lanzar consumers explícitamente (cuando hay broker)
	python -m alpespartners.modulos.pagos.infraestructura.consumidores &
	PAGOS_PID=$!
	python -m alpespartners.modulos.campanias.infraestructura.consumidores &
	CAMPANIAS_PID=$!
	python -m alpespartners.modulos.cliente.infraestructura.consumidores &
	CLIENTE_PID=$!

	echo "[ENTRYPOINT] Consumers lanzados: pagos=$PAGOS_PID campanias=$CAMPANIAS_PID cliente=$CLIENTE_PID"
fi

# Esperar a que Flask termine (mantiene el contenedor vivo)
wait $FLASK_PID
