"""Deprecated: La infraestructura fue migrada a `src/pagos/infraestructura`.

Este paquete se mantiene solo por compatibilidad temporal y no debe importarse.
"""

raise RuntimeError("Este paquete fue migrado a `pagos.infraestructura` y no debe importarse.")
# Lanzar poller de outbox al iniciar el microservicio (excepto en testing)
import os
if not os.getenv('TESTING', '').lower() == 'true':
	try:
		from alpespartners.modulos.pagos.infraestructura.outbox import outbox_poller
		interval = int(os.getenv('OUTBOX_POLL_INTERVAL_MS', '1000'))
		outbox_poller(interval_ms=interval)
	except Exception as e:
		import logging
		logging.error(f"No se pudo lanzar el poller de outbox: {e}")
