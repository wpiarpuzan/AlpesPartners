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
    def handle(self, comando: ProcesarPago):

        payout: Payout = Payout.crear(
            partner_id=comando.partner_id,
            cycle_id=comando.cycle_id
        )

        self._repo_payout: IPayoutRepositorio = FabricaRepositorio.crear_objeto(IPayoutRepositorio)
        self._repo_transacciones: ITransactionRepositorio = FabricaRepositorio.crear_objeto(ITransactionRepositorio)

        transacciones: list[Transaction] = self._repo_transacciones.obtener_por_partner_y_ciclo(
            partner_id=comando.partner_id,
            cycle_id=comando.cycle_id
        )

        if not transacciones:
            print(f"No se encontraron transacciones para el partner {comando.partner_id}, ciclo {comando.cycle_id}. No se procesará el pago.")
            return

        payout.calcular_comisiones(transacciones)
        UnidadTrabajoPuerto.registrar_batch(self._repo_payout.agregar, payout, mapeador=MapeadorPayout())
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        
        print(f"Payout para partner {payout.partner_id} procesado y listo para commit.")

@comando.register(ProcesarPago)
def ejecutar_comando_procesar_pago(comando: ProcesarPago):
    handler = ProcesarPagoHandler()
    handler.handle(comando)