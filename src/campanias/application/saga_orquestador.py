"""Wrapper migrado desde alpespartners.modulos.campanias.aplicacion.saga_orquestador
Se mantiene la lógica y se actualizan imports para el nuevo paquete."""
from campanias.application.dto import CrearCampaniaDTO
from campanias.application.servicio import CampaniasService
from campanias.domain.entidades import CampaniaAprobada, CampaniaCancelada
from campanias.infrastructure.event_store import append_event
from campanias.infrastructure.publisher import publish_event

def orchestrar_creacion(data):
    # ejemplo de orquestación simplificada
    cmd = CrearCampaniaDTO(**data)
    svc = CampaniasService()
    svc.handle_crear_campania(cmd)
