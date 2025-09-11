"""
Define los comandos y sus respectivos manejadores (handlers) para la capa de aplicación del módulo de pagos.
Estos componentes son responsables de orquestar los casos de uso y coordinar las interacciones
entre el dominio y la infraestructura.
"""

from dataclasses import dataclass
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.seedwork.aplicacion.comandos import Comando
from alpespartners.seedwork.aplicacion.comandos import ComandoHandler
from alpespartners.modulos.pagos.dominio.entidades import Payout, Transaction
from alpespartners.modulos.pagos.dominio.repositorios import IPayoutRepositorio, ITransactionRepositorio
from alpespartners.seedwork.infraestructura.uow import UnidadTrabajoPuerto
from alpespartners.modulos.pagos.infraestructura.fabricas import FabricaRepositorio
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

# ===================================
# Handlers
# ===================================

class ProcesarPagoHandler(ComandoHandler):
    def handle(self, payout_dto):
        fabrica = FabricaRepositorio()
        self._repo_payout: IPayoutRepositorio = fabrica.crear_objeto(IPayoutRepositorio)
        self._repo_transacciones: ITransactionRepositorio = fabrica.crear_objeto(ITransactionRepositorio)

        payout: Payout = Payout.crear(
            partner_id=payout_dto.partner_id,
            cycle_id=payout_dto.cycle_id,
            payment_method_type=payout_dto.payment_method_type,
            payment_method_mask=payout_dto.payment_method_mask
        )
        # Asignar campos adicionales del DTO al objeto de dominio
        if hasattr(payout, 'monto_total') and payout_dto.monto_total_valor:
            payout.monto_total.valor = payout_dto.monto_total_valor
        if hasattr(payout, 'monto_total') and payout_dto.monto_total_moneda:
            payout.monto_total.moneda = payout_dto.monto_total_moneda
        if hasattr(payout, 'confirmation_id'):
            payout.confirmation_id = payout_dto.confirmation_id
        if hasattr(payout, 'failure_reason'):
            payout.failure_reason = payout_dto.failure_reason
        if hasattr(payout, 'medio_pago') and payout_dto.payment_method_type:
            payout.medio_pago.tipo = payout_dto.payment_method_type
        if hasattr(payout, 'medio_pago') and payout_dto.payment_method_mask:
            payout.medio_pago.mask = payout_dto.payment_method_mask
        if payout_dto.processed_at:
            payout.processed_at = payout_dto.processed_at
        if payout_dto.completed_at:
            payout.completed_at = payout_dto.completed_at

        transacciones: list[Transaction] = self._repo_transacciones.obtener_por_partner_y_ciclo(
            partner_id=payout_dto.partner_id,
            cycle_id=payout_dto.cycle_id
        )

        if not transacciones:
            print(f"No se encontraron transacciones para el partner {payout_dto.partner_id}, ciclo {payout_dto.cycle_id}. No se procesará el pago.")
            return None

        payout.calcular_comisiones(transacciones)
        UnidadTrabajoPuerto.registrar_batch(self._repo_payout.agregar, payout)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        print(f"Payout para partner {payout.partner_id} procesado y listo para commit.")
        return payout

@comando.register(ProcesarPago)
def ejecutar_comando_procesar_pago(comando: ProcesarPago):
    handler = ProcesarPagoHandler()
    return handler.handle(comando)