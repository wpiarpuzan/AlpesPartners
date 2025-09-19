"""
Adaptador para el servicio de campañas

Este adaptador implementa la comunicación HTTP con las APIs REST del servicio
de campañas de Alpes Partners, convirtiendo entre los modelos del BFF y los del servicio.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from bff.application.ports import ICampaniaService
from bff.domain.models import CampaniaWeb, PaginatedResult, PaginationInfo, EstadoCampania
from bff.domain.exceptions import CampaniaNotFoundException, ServiceUnavailableException

# Cliente HTTP para comunicación con microservicios
from bff.infrastructure.http_client import CampaniaServiceHttpClient


class CampaniaServiceAdapter(ICampaniaService):
    """Adaptador para el servicio de campañas via HTTP"""
    
    def __init__(self, http_client: CampaniaServiceHttpClient):
        self.http_client = http_client
        self.service_name = "campanias"
        self.logger = logging.getLogger(__name__)
    
    async def obtener_campania(self, campania_id: str) -> Optional[CampaniaWeb]:
        """Obtiene una campaña por ID utilizando HTTP REST API"""
        try:
            data = await self.http_client.obtener_campania(campania_id)
            if not data:
                return None
            
            return self._convert_to_campania_web(data)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo campaña {campania_id}: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def listar_campanias(self, pagination: PaginationInfo, filtros: Dict[str, Any] = None) -> PaginatedResult:
        """Lista campañas con filtros y paginación"""
        try:
            campanias_mock = [
                CampaniaWeb(
                    id=f"CAMP{i:04d}",
                    cliente_id=f"cliente-{i:04d}",
                    cliente_nombre=f"Cliente Campaña {i}",
                    itinerario=[f"Ciudad {i}A", f"Ciudad {i}B", f"Ciudad {i}C"],
                    estado=EstadoCampania.APROBADA if i % 3 == 0 else EstadoCampania.CREADA,
                    fecha_creacion=datetime.now(),
                    fecha_aprobacion=datetime.now() if i % 3 == 0 else None,
                    pago_asociado_id=f"pago-{i:04d}" if i % 3 == 0 else None
                )
                for i in range(1, 31)  # 30 campañas simuladas
            ]
            
            # Aplicar filtros
            if filtros:
                if 'estado' in filtros:
                    campanias_mock = [c for c in campanias_mock if c.estado.value == filtros['estado']]
                if 'cliente_id' in filtros:
                    campanias_mock = [c for c in campanias_mock if c.cliente_id == filtros['cliente_id']]
            
            start_idx = (pagination.page - 1) * pagination.per_page
            end_idx = start_idx + pagination.per_page
            items = campanias_mock[start_idx:end_idx]
            
            pagination_info = PaginationInfo(
                page=pagination.page,
                per_page=pagination.per_page,
                total_items=len(campanias_mock),
                total_pages=(len(campanias_mock) + pagination.per_page - 1) // pagination.per_page,
                has_next=end_idx < len(campanias_mock),
                has_prev=pagination.page > 1
            )
            
            return PaginatedResult(items=items, pagination=pagination_info)
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def crear_campania(self, datos: Dict[str, Any]) -> CampaniaWeb:
        """Crea una nueva campaña utilizando HTTP REST API"""
        try:
            campania_data = await self.http_client.crear_campania(datos)
            return self._convert_to_campania_web(campania_data)
            
        except Exception as e:
            self.logger.error(f"Error creando campaña: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def obtener_campanias_por_cliente(self, cliente_id: str, limit: int = 10) -> List[CampaniaWeb]:
        """Obtiene campañas de un cliente"""
        try:
            campanias_cliente = [
                CampaniaWeb(
                    id=f"CAMP-{cliente_id[:8]}-{i:03d}",
                    cliente_id=cliente_id,
                    cliente_nombre=f"Cliente {cliente_id[:8]}",
                    itinerario=[f"Destino {i}A", f"Destino {i}B"],
                    estado=EstadoCampania.APROBADA if i % 2 == 0 else EstadoCampania.CREADA,
                    fecha_creacion=datetime.now(),
                    fecha_aprobacion=datetime.now() if i % 2 == 0 else None
                )
                for i in range(1, min(limit + 1, 4))  # Máximo 3 campañas por cliente
            ]
            
            return campanias_cliente
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def obtener_estadisticas_campanias(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales de campañas"""
        try:
            return {
                "total_campanias": 450,
                "campanias_activas": 123,
                "campanias_completadas": 287,
                "campanias_canceladas": 40,
                "promedio_itinerario": 3.2,
                "campanias_creadas_hoy": 12,
                "tasa_aprobacion": 0.85
            }
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    def _convert_to_campania_web(self, data: Dict[str, Any]) -> CampaniaWeb:
        """Convierte datos del servicio HTTP al modelo BFF"""
        # Mapeo de estados
        estado_mapping = {
            "CREADA": EstadoCampania.CREADA,
            "APROBADA": EstadoCampania.APROBADA,
            "CANCELADA": EstadoCampania.CANCELADA,
            "COMPLETADA": EstadoCampania.COMPLETADA
        }
        
        # Manejo de fechas
        fecha_creacion = None
        if data.get('fecha_creacion'):
            try:
                fecha_creacion = datetime.fromisoformat(data['fecha_creacion'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                fecha_creacion = datetime.now()
        
        fecha_aprobacion = None
        if data.get('fecha_aprobacion'):
            try:
                fecha_aprobacion = datetime.fromisoformat(data['fecha_aprobacion'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return CampaniaWeb(
            id=str(data['id']),
            cliente_id=str(data.get('cliente_id', '')),
            cliente_nombre=str(data.get('cliente_nombre', data.get('cliente_id', ''))),
            itinerario=data.get('itinerario', []),
            estado=estado_mapping.get(str(data.get('estado', 'CREADA')).upper(), EstadoCampania.CREADA),
            fecha_creacion=fecha_creacion or datetime.now(),
            fecha_aprobacion=fecha_aprobacion,
            pago_asociado_id=data.get('pago_asociado_id')
        )