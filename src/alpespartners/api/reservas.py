"""
FastAPI router for reservas module.

Usage examples:

POST /reservas/comandos/crear
curl -X POST http://localhost:8000/reservas/comandos/crear -H "Content-Type: application/json" -d '{"idReserva": "123", "idCliente": "456", "itinerario": ["FL123", "FL456"]}'

GET /reservas/{id}
curl http://localhost:8000/reservas/123
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from alpespartners.config.db import SessionLocal, engine
from alpespartners.modulos.reservas.infraestructura import repos as reservas_repos
from alpespartners.modulos.reservas.aplicacion.servicio import ReservasService
from alpespartners.modulos.reservas.aplicacion.dto import CrearReservaDTO
from alpespartners.modulos.reservas.infraestructura.mapeos import Base as ReservasBase
from alpespartners.modulos.reservas.infraestructura.proyecciones import Base as ProyeccionesBase
import logging

router = APIRouter(prefix="/reservas", tags=["reservas"])

# Ensure tables exist on startup
ReservasBase.metadata.create_all(bind=engine)
ProyeccionesBase.metadata.create_all(bind=engine)

# Dependency for DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/comandos/crear", status_code=202)
async def crear_reserva(cmd: CrearReservaDTO, db: Session = Depends(get_db)):
    """Encola comando CrearReserva y responde si fue encolado."""
    try:
        service = ReservasService(db)
        service.handle_crear_reserva(cmd)
        return {"enqueued": True}
    except Exception as e:
        logging.exception("Error en crear_reserva")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id_reserva}")
async def obtener_reserva(id_reserva: str, db: Session = Depends(get_db)):
    """Devuelve el estado de la reserva desde la proyección."""
    repo = reservas_repos.ReservaProyeccionRepo(db)
    reserva = repo.obtener_por_id(id_reserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

# TODO: Reutilizar middleware de métricas y manejo de errores si está disponible en seedwork.
