
"""
FastAPI router for campanias module.

Usage examples:

POST /campanias/comandos/crear
curl -X POST http://localhost:8000/campanias/comandos/crear -H "Content-Type: application/json" -d '{"idCampania": "123", "idCliente": "456", "itinerario": ["FL123", "FL456"]}'

GET /campanias/{id}
curl http://localhost:8000/campanias/123
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from alpespartners.config.db import SessionLocal, engine
from alpespartners.modulos.campanias.infraestructura import repos as campanias_repos
from alpespartners.modulos.campanias.aplicacion.servicio import CampaniasService
from alpespartners.modulos.campanias.aplicacion.dto import CrearCampaniaDTO
from alpespartners.modulos.campanias.infraestructura.mapeos import Base as CampaniasBase
from alpespartners.modulos.campanias.infraestructura.proyecciones import Base as ProyeccionesBase
import logging


router = APIRouter(prefix="/campanias", tags=["campanias"])

# Ensure tables exist on startup
CampaniasBase.metadata.create_all(bind=engine)
ProyeccionesBase.metadata.create_all(bind=engine)

# Dependency for DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/comandos/crear", status_code=202)
async def crear_campania(cmd: CrearCampaniaDTO, db: Session = Depends(get_db)):
    """Encola comando CrearCampania y responde si fue encolado."""
    try:
        service = CampaniasService(db)
        service.handle_crear_campania(cmd)
        return {"enqueued": True}
    except Exception as e:
        logging.exception("Error en crear_campania")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id_campania}")
async def obtener_campania(id_campania: str, db: Session = Depends(get_db)):
    """Devuelve el estado de la campania desde la proyección."""
    repo = campanias_repos.CampaniaProyeccionRepo(db)
    campania = repo.obtener_por_id(id_campania)
    if not campania:
        raise HTTPException(status_code=404, detail="Campania no encontrada")
    return campania

# TODO: Reutilizar middleware de métricas y manejo de errores si está disponible en seedwork.
