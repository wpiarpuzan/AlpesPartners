from dataclasses import dataclass
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.seedwork.aplicacion.comandos import Comando, ComandoHandler


@dataclass
class ProcesarPago(Comando):
    partner_id: str
    cycle_id: str
    total_amount: float
    currency: str
    confirmation_id: str
    failure_reason: str = None
    payment_method_type: str = None
    payment_method_mask: str = None
    processed_at: str = None
    completed_at: str = None


class ProcesarPagoHandler(ComandoHandler):
    def handle(self, comando: ProcesarPago):
        # Publicación simplificada a Pulsar sólo para pruebas locales
        import json, os
        print(f"[pagos] Simulated publish of ProcesarPago: {comando}")
        return 'ok'


@comando.register(ProcesarPago)
def ejecutar_comando_procesar_pago(comando: ProcesarPago):
    handler = ProcesarPagoHandler()
    return handler.handle(comando)
