"""
Adaptador para el servicio de clientes

Este adaptador implementa la comunicación HTTP con las APIs REST del servicio
de clientes de Alpes Partners, convirtiendo entre los modelos del BFF y los del servicio.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from bff.application.ports import IClienteService
from bff.domain.models import ClienteWeb, PaginatedResult, PaginationInfo, EstadoCliente
from bff.domain.exceptions import ClienteNotFoundException, ServiceUnavailableException

# Cliente HTTP para comunicación con microservicios
from bff.infrastructure.http_client import ClienteServiceHttpClient


class ClienteServiceAdapter(IClienteService):
    """Adaptador para el servicio de clientes via HTTP"""
    
    def __init__(self, http_client: ClienteServiceHttpClient):
        self.http_client = http_client
        self.service_name = "cliente"
        self.logger = logging.getLogger(__name__)
    
    async def obtener_cliente(self, cliente_id: str) -> Optional[ClienteWeb]:
        """Obtiene un cliente por ID utilizando HTTP REST API"""
        try:
            data = await self.http_client.obtener_cliente(cliente_id)
            if not data:
                return None
            
            return self._convert_to_cliente_web(data)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo cliente {cliente_id}: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def listar_clientes(self, pagination: PaginationInfo) -> PaginatedResult:
        """Lista clientes con paginación"""
        try:
            # El servicio backend no tiene endpoint de listado aún, usamos mock
            self.logger.warning("Endpoint de listado no disponible en servicio backend, usando datos mock")
            
            clientes_mock = [
                ClienteWeb(
                    id=str(uuid.uuid4()),
                    nombre=f"Cliente {i}",
                    email=f"cliente{i}@example.com",
                    cedula=f"1234567{i}",
                    fecha_registro=datetime.now(),
                    estado=EstadoCliente.ACTIVO,
                    total_pagos=i * 2,
                    campanias_activas=1
                )
                for i in range(1, 26)  # 25 clientes simulados
            ]
            
            start_idx = (pagination.page - 1) * pagination.per_page
            end_idx = start_idx + pagination.per_page
            items = clientes_mock[start_idx:end_idx]
            
            pagination_info = PaginationInfo(
                page=pagination.page,
                per_page=pagination.per_page,
                total_items=len(clientes_mock),
                total_pages=(len(clientes_mock) + pagination.per_page - 1) // pagination.per_page,
                has_next=end_idx < len(clientes_mock),
                has_prev=pagination.page > 1
            )
            
            return PaginatedResult(items=items, pagination=pagination_info)
            
        except Exception as e:
            self.logger.error(f"Error listando clientes: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def crear_cliente(self, datos: Dict[str, Any]) -> ClienteWeb:
        """Crea un nuevo cliente utilizando HTTP REST API"""
        try:
            # Agregar ID si no existe
            if 'id' not in datos:
                datos['id'] = str(uuid.uuid4())
            
            cliente_data = await self.http_client.crear_cliente(datos)
            
            return self._convert_to_cliente_web(cliente_data)
            
        except Exception as e:
            self.logger.error(f"Error creando cliente: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def buscar_clientes(self, termino: str, pagination: PaginationInfo) -> PaginatedResult:
        """Busca clientes por término (implementación mock)"""
        # En producción, se implementaría una búsqueda real
        all_clients = await self.listar_clientes(PaginationInfo(page=1, per_page=100))
        
        # Filtrar por término de búsqueda
        filtered_clients = [
            cliente for cliente in all_clients.items
            if termino.lower() in cliente.nombre.lower() or 
                termino.lower() in cliente.email.lower()
        ]
        
        start_idx = (pagination.page - 1) * pagination.per_page
        end_idx = start_idx + pagination.per_page
        items = filtered_clients[start_idx:end_idx]
        
        pagination_info = PaginationInfo(
            page=pagination.page,
            per_page=pagination.per_page,
            total_items=len(filtered_clients),
            total_pages=(len(filtered_clients) + pagination.per_page - 1) // pagination.per_page,
            has_next=end_idx < len(filtered_clients),
            has_prev=pagination.page > 1
        )
        
        return PaginatedResult(items=items, pagination=pagination_info)
    
    async def obtener_estadisticas_cliente(self, cliente_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas específicas del cliente"""
        cliente = await self.obtener_cliente(cliente_id)
        if not cliente:
            raise ClienteNotFoundException(cliente_id)
        
        # Estadísticas mock - en producción se calcularían desde eventos/datos reales
        return {
            "total_pagos": cliente.total_pagos,
            "monto_total": float(cliente.monto_total_pagos),
            "promedio_pago": float(cliente.monto_total_pagos) / max(cliente.total_pagos, 1),
            "campanias_activas": cliente.campanias_activas,
            "ultimo_pago": cliente.ultimo_pago.isoformat() if cliente.ultimo_pago else None,
            "dias_desde_registro": (datetime.now() - cliente.fecha_registro).days if cliente.fecha_registro else 0
        }
    
    def _convert_to_cliente_web(self, data: Dict[str, Any]) -> ClienteWeb:
        """Convierte datos del servicio HTTP al modelo BFF"""
        # Manejo de fechas con múltiples formatos posibles
        fecha_registro = None
        if data.get('fecha_registro'):
            fecha_str = data['fecha_registro']
            if isinstance(fecha_str, str):
                try:
                    fecha_registro = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                except ValueError:
                    fecha_registro = datetime.now()
        
        ultimo_pago = None
        if data.get('ultimo_pago'):
            ultimo_str = data['ultimo_pago']
            if isinstance(ultimo_str, str):
                try:
                    ultimo_pago = datetime.fromisoformat(ultimo_str.replace('Z', '+00:00'))
                except ValueError:
                    pass
        
        return ClienteWeb(
            id=str(data['id']),
            nombre=data['nombre'],
            email=data['email'],
            cedula=str(data.get('cedula', '')),
            fecha_registro=fecha_registro or datetime.now(),
            estado=EstadoCliente.ACTIVO,  # Por defecto activo
            total_pagos=int(data.get('total_pagos', 0)),
            ultimo_pago=ultimo_pago
        )