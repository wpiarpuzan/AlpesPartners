from pagos.aplicacion.dto import PayoutDTO

class MapeadorPayoutDTOJson:
    def externo_a_dto(self, data):
        return PayoutDTO(**data)
