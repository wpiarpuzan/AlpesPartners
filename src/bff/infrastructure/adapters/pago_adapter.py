"""
Adaptador para el servicio de pagos

Este adaptador implementa la comunicación directa con el módulo de pagos
de Alpes Partners, convirtiendo entre los modelos del BFF y los del servicio.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from bff.application.ports import IPagoService
from bff.domain.models import PagoWeb, PaginatedResult, PaginationInfo, EstadoPago
from bff.domain.exceptions import PagoNotFoundException, ServiceUnavailableException

# Imports de servicios existentes de Alpes Partners
from alpespartners.seedwork.aplicacion.queries import ejecutar_query
from alpespartners.modulos.pagos.aplicacion.queries.obtener_pago import ObtenerPayout
from alpespartners.modulos.pagos.aplicacion.mapeadores import MapeadorPayoutDTOJson


class PagoServiceAdapter(IPagoService):
    """Adaptador para el servicio de pagos interno"""
    
    def __init__(self):
        self.service_name = "pagos"
        self.mapeador = MapeadorPayoutDTOJson()
    
    async def obtener_pago(self, pago_id: str) -> Optional[PagoWeb]:
        """Obtiene un pago por ID utilizando el servicio interno"""
        try:
            query_resultado = await asyncio.get_event_loop().run_in_executor(
                None, ejecutar_query, ObtenerPayout(id=pago_id)
            )
            
            if not query_resultado.resultado:
                return None
            
            return self._convert_to_pago_web(query_resultado.resultado)
            
        except Exception as e:
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
        """Crea un nuevo pago (implementación mock)"""
        try:
            # En producción se usaría el comando ProcesarPago
            nuevo_pago = PagoWeb(
                id=f"payout-{uuid.uuid4().hex[:8]}",
                partner_id=datos['partner_id'],
                cliente_nombre=datos.get('cliente_nombre'),
                monto=Decimal(str(datos['monto'])),
                moneda=datos.get('moneda', 'USD'),
                estado=EstadoPago.PENDIENTE,
                fecha_creacion=datetime.now(),
                metodo_pago=datos.get('metodo_pago', 'CREDIT_CARD')
            )
            
            return nuevo_pago
            
        except Exception as e:
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
    
    def _convert_to_pago_web(self, payout_dto) -> PagoWeb:
        """Convierte DTO interno al modelo BFF"""
        estado_mapping = {
            "PENDIENTE": EstadoPago.PENDIENTE,
            "CALCULADO": EstadoPago.PROCESANDO,
            "EN_PROCESO": EstadoPago.PROCESANDO,
            "EXITOSO": EstadoPago.COMPLETADO,
            "FALLIDO": EstadoPago.FALLIDO
        }
        
        return PagoWeb(
            id=payout_dto.id,
            partner_id=payout_dto.partner_id,
            monto=payout_dto.monto_total_valor or Decimal('0'),
            moneda=payout_dto.monto_total_moneda or "USD",
            estado=estado_mapping.get(payout_dto.estado, EstadoPago.PENDIENTE),
            fecha_creacion=payout_dto.fecha_creacion,
            metodo_pago=payout_dto.payment_method_type,
            confirmation_id=payout_dto.confirmation_id
        )