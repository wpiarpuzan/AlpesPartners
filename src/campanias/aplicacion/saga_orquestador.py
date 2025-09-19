from campanias.application.servicio import CampaniasService


class CampaniasSagaOrquestador:
    @staticmethod
    def handle_event(event):
        # Delegar a servicio
        service = CampaniasService()
        return service.handle_event(event)
