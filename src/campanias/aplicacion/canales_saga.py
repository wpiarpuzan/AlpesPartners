from campanias.application.saga_orquestador import CampaniasSagaOrquestador


def canales_para_saga():
    return {
        'eventos.campanias': CampaniasSagaOrquestador.handle_event,
    }
