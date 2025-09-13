"""
Adaptador para el servicio de pagos

Este adaptador implementa la comunicación HTTP con las APIs REST del servicio
de pagos de Alpes Partners, convirtiendo entre los modelos del BFF y los del servicio.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid
import logging

from bff.application.ports import IPagoService
from bff.domain.models import PagoWeb, PaginatedResult, PaginationInfo, EstadoPago
from bff.domain.exceptions import PagoNotFoundException, ServiceUnavailableException

# Cliente HTTP para comunicación con microservicios
from bff.infrastructure.http_client import PagoServiceHttpClient


class PagoServiceAdapter(IPagoService):
    """Adaptador para el servicio de pagos via HTTP"""
    
    def __init__(self, http_client: PagoServiceHttpClient):
        self.http_client = http_client
        self.service_name = "pagos"
        self.logger = logging.getLogger(__name__)
    
    async def obtener_pago(self, pago_id: str) -> Optional[PagoWeb]:
        """Obtiene un pago por ID utilizando HTTP REST API"""
        try:
            data = await self.http_client.obtener_pago(pago_id)
            if not data:
                return None
            
            return self._convert_to_pago_web(data)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo pago {pago_id}: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def listar_pagos(self, pagination: PaginationInfo, filtros: Dict[str, Any] = None) -> PaginatedResult:
        """Lista pagos con filtros y paginación"""
        try:
            # Simulación de pagos - en producción se implementaría query con paginación
            pagos_mock = [
                PagoWeb(
                    id=f"payout-{i:04d}",
                    partner_id=f"PARTNER{i:03d}",
                    cliente_nombre=f"Cliente Partner {i}",
                    monto=Decimal(str(1000 + i * 100)),
                    moneda="USD",
                    estado=EstadoPago.COMPLETADO if i % 3 == 0 else EstadoPago.PROCESANDO,
                    fecha_creacion=datetime.now(),
                    metodo_pago="CREDIT_CARD",
                    confirmation_id=f"CONF-{i:06d}" if i % 3 == 0 else None
                )
                for i in range(1, 51)  # 50 pagos simulados
            ]
            
            # Aplicar filtros si existen
            if filtros:
                if 'estado' in filtros:
                    pagos_mock = [p for p in pagos_mock if p.estado.value == filtros['estado']]
                if 'partner_id' in filtros:
                    pagos_mock = [p for p in pagos_mock if filtros['partner_id'].lower() in p.partner_id.lower()]
            
            start_idx = (pagination.page - 1) * pagination.per_page
            end_idx = start_idx + pagination.per_page
            items = pagos_mock[start_idx:end_idx]
            
            pagination_info = PaginationInfo(
                page=pagination.page,
                per_page=pagination.per_page,
                total_items=len(pagos_mock),
                total_pages=(len(pagos_mock) + pagination.per_page - 1) // pagination.per_page,
                has_next=end_idx < len(pagos_mock),
                has_prev=pagination.page > 1
            )
            
            return PaginatedResult(items=items, pagination=pagination_info)
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def crear_pago(self, datos: Dict[str, Any]) -> PagoWeb:
        """Crea un nuevo pago utilizando HTTP REST API"""
        try:
            pago_data = await self.http_client.crear_pago(datos)
            return self._convert_to_pago_web(pago_data)
            
        except Exception as e:
            self.logger.error(f"Error creando pago: {str(e)}")
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def obtener_pagos_por_cliente(self, cliente_id: str, limit: int = 10) -> List[PagoWeb]:
        """Obtiene pagos recientes de un cliente"""
        try:
            # En producción se implementaría query específica
            # Por ahora simulamos pagos del cliente
            pagos_cliente = [
                PagoWeb(
                    id=f"payout-cliente-{cliente_id}-{i}",
                    partner_id=f"PARTNER-{cliente_id[:8]}",
                    cliente_nombre=f"Cliente {cliente_id[:8]}",
                    monto=Decimal(str(500 + i * 150)),
                    moneda="USD",
                    estado=EstadoPago.COMPLETADO if i % 2 == 0 else EstadoPago.PROCESANDO,
                    fecha_creacion=datetime.now(),
                    metodo_pago="CREDIT_CARD"
                )
                for i in range(1, min(limit + 1, 6))  # Máximo 5 pagos por cliente
            ]
            
            return pagos_cliente
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    async def obtener_estadisticas_pagos(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales de pagos"""
        try:
            # Simulación de estadísticas - en producción se calcularían desde datos reales
            return {
                "total_pagos": 1250,
                "monto_total_procesado": 2850000.50,
                "pagos_pendientes": 45,
                "pagos_procesando": 23,
                "pagos_completados": 1182,
                "pagos_fallidos": 15,
                "promedio_monto": 2280.00,
                "transacciones_hoy": 67
            }
            
        except Exception as e:
            raise ServiceUnavailableException(self.service_name, str(e))
    
    def _convert_to_pago_web(self, data: Dict[str, Any]) -> PagoWeb:
        """Convierte datos HTTP al modelo BFF"""
        estado_mapping = {
            "PENDIENTE": EstadoPago.PENDIENTE,
            "CALCULADO": EstadoPago.PROCESANDO,
            "EN_PROCESO": EstadoPago.PROCESANDO,
            "EXITOSO": EstadoPago.COMPLETADO,
            "COMPLETADO": EstadoPago.COMPLETADO,
            "FALLIDO": EstadoPago.FALLIDO
        }
        
        # Manejo de fechas
        fecha_creacion = None
        if data.get('fecha_creacion'):
            fecha_str = data['fecha_creacion']
            if isinstance(fecha_str, str):
                try:
                    fecha_creacion = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                except ValueError:
                    fecha_creacion = datetime.now()
        
        # Determinar el monto (puede venir en diferentes campos según el endpoint)
        monto = Decimal('0')
        if 'monto_total' in data:
            monto = Decimal(str(data['monto_total']))
        elif 'monto' in data:
            monto = Decimal(str(data['monto']))
        elif 'total_amount' in data:
            monto = Decimal(str(data['total_amount']))
        
        return PagoWeb(
            id=str(data['id']),
            partner_id=str(data.get('partner_id', '')),
            cliente_nombre=str(data.get('cliente_nombre', data.get('partner_id', ''))),
            monto=monto,
            moneda=str(data.get('moneda', data.get('currency', 'USD'))),
            estado=estado_mapping.get(str(data.get('estado', 'PENDIENTE')).upper(), EstadoPago.PENDIENTE),
            fecha_creacion=fecha_creacion or datetime.now(),
            metodo_pago=str(data.get('metodo_pago', data.get('payment_method_type', 'CREDIT_CARD'))),
            confirmation_id=data.get('confirmation_id')
        )