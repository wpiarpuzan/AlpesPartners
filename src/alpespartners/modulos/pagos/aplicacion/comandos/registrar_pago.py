from dataclasses import dataclass
from decimal import Decimal
from alpespartners.modulos.pagos.dominio.entidades import Pago
from alpespartners.modulos.pagos.dominio.objetos_valor import Monto, MedioPago, TipoMedioPago
from alpespartners.modulos.pagos.dominio.repositorios import IPagoRepositorio

@dataclass
class RegistrarPago:
    reserva_id: str
    cliente_id: str 
    valor: float
    moneda: str
    medio_tipo: str   # viene como texto en el request
    medio_mask: str

class RegistrarPagoHandler:
    def __init__(self, repo: IPagoRepositorio, publicar_evento):
        self.repo = repo
        self.publicar_evento = publicar_evento

    def handle(self, cmd: RegistrarPago) -> str:
        # convertir string -> Enum (lanza ValueError si no existe)
        try:
            tipo_enum = TipoMedioPago(cmd.medio_tipo.upper())
        except ValueError:
            opciones = [e.value for e in TipoMedioPago]
            raise ValueError(f"medio_tipo inválido: {cmd.medio_tipo}. Opciones: {opciones}")

        pago = Pago.registrar(
            cmd.reserva_id,
            cmd.cliente_id, 
            Monto(Decimal(cmd.valor), cmd.moneda),
            MedioPago(tipo_enum, cmd.medio_mask),
        )
        self.repo.agregar(pago)
        for ev in pago.eventos:
            self.publicar_evento(ev)
        return pago.id
