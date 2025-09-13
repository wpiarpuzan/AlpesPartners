"""
Casos de uso específicos para UI Web

Estos casos de uso orquestan múltiples servicios backend para proporcionar
funcionalidades optimizadas para interfaces web.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal

from bff.application.ports import IClienteService, IPagoService, ICampaniaService, ICacheService, ILoggerService
from bff.domain.models import (
    ClienteWeb, PagoWeb, CampaniaWeb, DashboardData, ClienteDetalle, 
    PaginatedResult, PaginationInfo
)
from bff.domain.exceptions import (
    ClienteNotFoundException, ValidationException, PaginationException
)


class DashboardUseCase:
    """Caso de uso para obtener datos del dashboard principal"""
    
    def __init__(
        self,
        cliente_service: IClienteService,
        pago_service: IPagoService,
        campania_service: ICampaniaService,
        cache_service: ICacheService,
        logger_service: ILoggerService
    ):
        self.cliente_service = cliente_service
        self.pago_service = pago_service
        self.campania_service = campania_service
        self.cache_service = cache_service
        self.logger = logger_service
    
    async def obtener_datos_dashboard(self) -> DashboardData:
        """Obtiene datos agregados para el dashboard"""
        cache_key = "dashboard_data"
        
        # Intentar obtener del caché primero
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            self.logger.debug("Dashboard data obtenido del caché")
            return cached_data
        
        try:
            # Obtener estadísticas de todos los servicios en paralelo
            import asyncio
            
            cliente_stats_task = self.cliente_service.obtener_estadisticas_cliente("global")
            pago_stats_task = self.pago_service.obtener_estadisticas_pagos()
            campania_stats_task = self.campania_service.obtener_estadisticas_campanias()
            
            # Ejecutar tareas en paralelo con manejo de excepciones
            results = await asyncio.gather(
                cliente_stats_task,
                pago_stats_task, 
                campania_stats_task,
                return_exceptions=True
            )
            
            cliente_stats = results[0] if not isinstance(results[0], Exception) else {}
            pago_stats = results[1] if not isinstance(results[1], Exception) else {}
            campania_stats = results[2] if not isinstance(results[2], Exception) else {}
            
            dashboard_data = DashboardData(
                total_clientes=cliente_stats.get('total_clientes', 0),
                clientes_activos=cliente_stats.get('clientes_activos', 0),
                total_pagos=pago_stats.get('total_pagos', 0),
                monto_total_procesado=Decimal(str(pago_stats.get('monto_total_procesado', 0))),
                pagos_pendientes=pago_stats.get('pagos_pendientes', 0),
                campanias_activas=campania_stats.get('campanias_activas', 0),
                campanias_completadas=campania_stats.get('campanias_completadas', 0)
            )
            
            # Guardar en caché por 5 minutos
            await self.cache_service.set(cache_key, dashboard_data, ttl_seconds=300)
            
            self.logger.info("Dashboard data generado exitosamente")
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos dashboard: {str(e)}")
            # Retornar dashboard vacío en caso de error
            return DashboardData()


class ClienteDetalleUseCase:
    """Caso de uso para obtener vista detallada de cliente"""
    
    def __init__(
        self,
        cliente_service: IClienteService,
        pago_service: IPagoService,
        campania_service: ICampaniaService,
        cache_service: ICacheService,
        logger_service: ILoggerService
    ):
        self.cliente_service = cliente_service
        self.pago_service = pago_service
        self.campania_service = campania_service
        self.cache_service = cache_service
        self.logger = logger_service
    
    async def obtener_detalle_cliente(self, cliente_id: str) -> ClienteDetalle:
        """Obtiene vista completa del cliente con datos relacionados"""
        if not cliente_id:
            raise ValidationException("cliente_id", "ID de cliente es requerido")
        
        cache_key = f"cliente_detalle_{cliente_id}"
        
        # Intentar caché primero
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            self.logger.debug(f"Detalle cliente {cliente_id} obtenido del caché")
            return cached_data
        
        try:
            # Obtener datos del cliente
            cliente = await self.cliente_service.obtener_cliente(cliente_id)
            if not cliente:
                raise ClienteNotFoundException(cliente_id)
            
            # Obtener datos relacionados en paralelo
            import asyncio
            
            pagos_task = self.pago_service.obtener_pagos_por_cliente(cliente_id, limit=5)
            campanias_task = self.campania_service.obtener_campanias_por_cliente(cliente_id, limit=5)
            estadisticas_task = self.cliente_service.obtener_estadisticas_cliente(cliente_id)
            
            pagos_recientes, campanias_recientes, estadisticas = await asyncio.gather(
                pagos_task, campanias_task, estadisticas_task,
                return_exceptions=True
            )
            
            # Manejar excepciones en tasks individuales
            pagos_recientes = pagos_recientes if not isinstance(pagos_recientes, Exception) else []
            campanias_recientes = campanias_recientes if not isinstance(campanias_recientes, Exception) else []
            estadisticas = estadisticas if not isinstance(estadisticas, Exception) else {}
            
            detalle = ClienteDetalle(
                cliente=cliente,
                pagos_recientes=pagos_recientes,
                campanias_recientes=campanias_recientes,
                estadisticas=estadisticas
            )
            
            # Guardar en caché por 2 minutos
            await self.cache_service.set(cache_key, detalle, ttl_seconds=120)
            
            self.logger.info(f"Detalle cliente {cliente_id} generado exitosamente")
            return detalle
            
        except ClienteNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"Error obteniendo detalle cliente {cliente_id}: {str(e)}")
            raise


class BusquedaIntegradaUseCase:
    """Caso de uso para búsqueda integrada en múltiples servicios"""
    
    def __init__(
        self,
        cliente_service: IClienteService,
        pago_service: IPagoService,
        campania_service: ICampaniaService,
        logger_service: ILoggerService
    ):
        self.cliente_service = cliente_service
        self.pago_service = pago_service
        self.campania_service = campania_service
        self.logger = logger_service
    
    async def buscar_global(
        self, 
        termino: str, 
        tipos: List[str] = None,
        pagination: PaginationInfo = None
    ) -> Dict[str, Any]:
        """Realiza búsqueda en múltiples servicios"""
        if not termino or len(termino.strip()) < 2:
            raise ValidationException("termino", "Término de búsqueda debe tener al menos 2 caracteres")
        
        if pagination is None:
            pagination = PaginationInfo(page=1, per_page=10)
        
        tipos = tipos or ["clientes", "pagos", "campanias"]
        resultados = {}
        
        try:
            import asyncio
            
            tasks = {}
            
            if "clientes" in tipos:
                tasks["clientes"] = self.cliente_service.buscar_clientes(termino, pagination)
            
            if "pagos" in tipos:
                filtros = {"partner_id": termino} if termino else None
                tasks["pagos"] = self.pago_service.listar_pagos(pagination, filtros)
            
            if "campanias" in tipos:
                filtros = {"cliente_id": termino} if termino else None
                tasks["campanias"] = self.campania_service.listar_campanias(pagination, filtros)
            
            # Ejecutar búsquedas en paralelo
            results = await asyncio.gather(
                *tasks.values(),
                return_exceptions=True
            )
            
            # Procesar resultados
            for i, tipo in enumerate(tasks.keys()):
                if not isinstance(results[i], Exception):
                    resultados[tipo] = results[i]
                else:
                    self.logger.warning(f"Error en búsqueda de {tipo}: {str(results[i])}")
                    resultados[tipo] = PaginatedResult(items=[], pagination=pagination)
            
            self.logger.info(f"Búsqueda global completada para término: {termino}")
            return {
                "termino": termino,
                "resultados": resultados,
                "total_encontrados": sum(r.pagination.total_items for r in resultados.values())
            }
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda global: {str(e)}")
            raise


class ValidacionUseCase:
    """Caso de uso para validaciones comunes"""
    
    @staticmethod
    def validar_paginacion(page: int, per_page: int) -> PaginationInfo:
        """Valida y normaliza parámetros de paginación"""
        if page < 1:
            raise PaginationException("Página debe ser mayor a 0")
        
        if per_page < 1 or per_page > 100:
            raise PaginationException("Items por página debe estar entre 1 y 100")
        
        return PaginationInfo(page=page, per_page=per_page)
    
    @staticmethod
    def validar_campos_requeridos(datos: Dict[str, Any], campos: List[str]) -> None:
        """Valida que campos requeridos estén presentes"""
        for campo in campos:
            if campo not in datos or not datos[campo]:
                raise ValidationException(campo, f"Campo {campo} es requerido")