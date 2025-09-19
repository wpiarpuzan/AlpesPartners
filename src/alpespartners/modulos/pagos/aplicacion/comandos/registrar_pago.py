"""
Define los comandos y sus respectivos manejadores (handlers) para la capa de aplicación del módulo de pagos.
Estos componentes son responsables de orquestar los casos de uso y coordinar las interacciones
entre el dominio y la infraestructura.
"""

from dataclasses import dataclass
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.seedwork.aplicacion.comandos import Comando
from alpespartners.seedwork.aplicacion.comandos import ComandoHandler
from alpespartners.modulos.pagos.aplicacion.mapeadores import MapeadorPayout

# ===================================
# Comandos
# ===================================

@dataclass
class ProcesarPago(Comando):
    """
    Comando para iniciar el caso de uso de procesamiento de un pago a un socio para un ciclo específico.
    """
    partner_id: str
    cycle_id: str
    total_amount: float
    currency: str
    confirmation_id: str
    failure_reason: str = None
    payment_method_type: str = None
    payment_method_mask: str = None
    """Deprecated: Migrado a `src/pagos`.

    Este archivo se deja como marcador temporal y no debe usarse.
    """

    raise RuntimeError("Este módulo fue migrado a `pagos` y no debe usarse.")
    processed_at: str = None
    completed_at: str = None

# ===================================
# Handlers
# ===================================

class ProcesarPagoHandler(ComandoHandler):
    def handle(self, comando):
        # Solo publicar el comando en Pulsar
        import pulsar, json, logging, os
        logging.basicConfig(level=logging.INFO, force=True)
        PULSAR_BROKER_URL = os.environ['PULSAR_BROKER_URL']
        TOPIC_COMANDOS_PAGOS = 'persistent://public/default/comandos-pagos'
        client = pulsar.Client(PULSAR_BROKER_URL)
        producer = client.create_producer(TOPIC_COMANDOS_PAGOS)
        mensaje = {'type': 'ProcesarPago', 'data': comando.__dict__}
        producer.send(json.dumps(mensaje).encode('utf-8'))
        print(f"[PULSAR][PUBLICACION][COMANDO] Comando publicado en Pulsar: {mensaje}")
        client.close()
        return 'ok'

@comando.register(ProcesarPago)
def ejecutar_comando_procesar_pago(comando: ProcesarPago):
    handler = ProcesarPagoHandler()
    return handler.handle(comando)