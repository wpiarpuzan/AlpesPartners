"""
Adaptador para el servicio de clientes

Este adaptador implementa la comunicación directa con el módulo de clientes
de Alpes Partners, convirtiendo entre los modelos del BFF y los del servicio.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from bff.application.ports import IClienteService
from bff.domain.models import ClienteWeb, PaginatedResult, PaginationInfo, EstadoCliente
from bff.domain.exceptions import ClienteNotFoundException, ServiceUnavailableException

# Imports de servicios existentes de Alpes Partners
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando
from alpespartners.seedwork.aplicacion.queries import ejecutar_query
from alpespartners.modulos.cliente.aplicacion.comandos.registrar_cliente import RegistrarCliente
from alpespartners.modulos.cliente.aplicacion.queries.obtener_cliente import ObtenerClientePorId


class ClienteServiceAdapter(IClienteService):
    """Adaptador para el servicio de clientes interno"""
    
    def __init__(self):
        self.service_name = "cliente"
    
    async def obtener_cliente(self, cliente_id: str) -> Optional[ClienteWeb]:
        """Obtiene un cliente por ID utilizando el servicio interno"""
        try:
            # Ejecutar query de forma síncrona y convertir a async
            query_resultado = await asyncio.get_event_loop().run_in_executor(
                None, ejecutar_query, ObtenerClientePorId(cliente_id)
            )
            
            if not query_resultado.resultado:
                return None
            
            data = query_resultado.resultado
            return self._convert_to_cliente_web(data)
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def listar_clientes(self, pagination: PaginationInfo) -> PaginatedResult:
        """Lista clientes con paginación (simulado por ahora)"""
        try:
            # Por ahora simulamos datos, en producción se implementaría
            # una query específica con paginación
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
                for i in range(1, 11)
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
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def crear_cliente(self, datos: Dict[str, Any]) -> ClienteWeb:
        """Crea un nuevo cliente utilizando el comando interno"""
        try:
            comando = RegistrarCliente(
                id=datos.get('id', str(uuid.uuid4())),
                nombre=datos['nombre'],
                email=datos['email'],
                cedula=datos['cedula'],
                fecha_nacimiento=datos['fecha_nacimiento']
            )
            
            cliente_creado = await asyncio.get_event_loop().run_in_executor(
                None, ejecutar_commando, comando
            )
            
            # Convertir el resultado del comando a ClienteWeb
            return ClienteWeb(
                id=str(cliente_creado.id),
                nombre=cliente_creado.nombre,
                email=cliente_creado.email.valor if hasattr(cliente_creado.email, 'valor') else cliente_creado.email,
                cedula=cliente_creado.cedula.numero if hasattr(cliente_creado.cedula, 'numero') else str(cliente_creado.cedula),
                fecha_registro=cliente_creado.fecha_registro,
                estado=EstadoCliente.ACTIVO,
                total_pagos=0
            )
            
        except Exception as e:
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
        """Convierte datos del servicio interno al modelo BFF"""
        return ClienteWeb(
            id=data['id'],
            nombre=data['nombre'],
            email=data['email'],
            cedula=data.get('cedula'),
            fecha_registro=datetime.fromisoformat(data['fecha_registro']) if data.get('fecha_registro') else None,
            estado=EstadoCliente.ACTIVO,  # Por defecto activo
            total_pagos=data.get('total_pagos', 0),
            ultimo_pago=datetime.fromisoformat(data['ultimo_pago']) if data.get('ultimo_pago') else None
        )