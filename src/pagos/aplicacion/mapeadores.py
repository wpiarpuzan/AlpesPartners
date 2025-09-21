from pagos.aplicacion.dto import PayoutDTO
from dataclasses import fields


class MapeadorPayoutDTOJson:
    def externo_a_dto(self, data: dict) -> PayoutDTO:
        """Map an external JSON dict to PayoutDTO.

        Ignore extra keys (e.g. campania_id) that are not defined on PayoutDTO.
        """
        allowed = {f.name for f in fields(PayoutDTO)}
        filtered = {k: v for k, v in data.items() if k in allowed}
        return PayoutDTO(**filtered)
