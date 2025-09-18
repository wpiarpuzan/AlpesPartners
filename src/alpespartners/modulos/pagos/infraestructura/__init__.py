# Lanzar poller de outbox al iniciar el microservicio (excepto en testing)
import os

# The outbox poller should only be started explicitly. When running the web
# dyno we must NOT start the poller (worker dyno runs it). Set START_OUTBOX_POLLER
# to 'true' or run with MESSAGE_BUS=DB_OUTBOX and RUN_AS_WORKER=1 to start it.
if not os.getenv('TESTING', '').lower() == 'true':
	start_flag = os.getenv('START_OUTBOX_POLLER', '').lower() == 'true'
	run_as_worker = os.getenv('RUN_AS_WORKER', '') == '1'
	message_bus = os.getenv('MESSAGE_BUS', '')
	should_start = start_flag or (message_bus == 'DB_OUTBOX' and run_as_worker)
	if should_start:
		try:
			from alpespartners.modulos.pagos.infraestructura.outbox import outbox_poller
			interval = int(os.getenv('OUTBOX_POLL_INTERVAL_MS', '1000'))
			outbox_poller(interval_ms=interval)
		except Exception as e:
			import logging
			logging.error(f"No se pudo lanzar el poller de outbox: {e}")
