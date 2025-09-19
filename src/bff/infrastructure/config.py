"""
Configurador de dependencias para el BFF

Implementa el patrón Dependency Injection para configurar
todas las dependencias de la aplicación.
"""

import os
import logging

from bff.application.ports import IClienteService, IPagoService, ICampaniaService, ICacheService, ILoggerService
from bff.infrastructure.adapters.cliente_adapter import ClienteServiceAdapter
from bff.infrastructure.adapters.pago_adapter import PagoServiceAdapter
from bff.infrastructure.adapters.campania_adapter import CampaniaServiceAdapter
from bff.infrastructure.adapters import InMemoryCacheAdapter, PythonLoggerAdapter
from bff.application.use_cases import (
    DashboardUseCase, ClienteDetalleUseCase, BusquedaIntegradaUseCase, ValidacionUseCase
)
from bff.infrastructure.http_client import HttpClientFactory


class DIContainer:
    """Contenedor de inyección de dependencias"""
    
    def __init__(self):
        # Configuración de URLs de servicios backend
        self.alpespartners_base_url = os.environ.get('ALPESPARTNERS_SERVICE_URL', 'http://localhost:5000')
        self.http_timeout = int(os.getenv('BFF_HTTP_TIMEOUT', '30'))
        
        # Servicios de infraestructura
        self._logger_service = PythonLoggerAdapter("bff")
        self._cache_service = InMemoryCacheAdapter()
        
        # Clientes HTTP para servicios backend
        self._cliente_http_client = HttpClientFactory.create_cliente_client(
            self.alpespartners_base_url, self.http_timeout
        )
        self._pago_http_client = HttpClientFactory.create_pago_client(
            self.alpespartners_base_url, self.http_timeout
        )
        self._campania_http_client = HttpClientFactory.create_campania_client(
            self.alpespartners_base_url, self.http_timeout
        )
        
        # Adaptadores de servicios backend (usando clientes HTTP)
        self._cliente_service = ClienteServiceAdapter(self._cliente_http_client)
        self._pago_service = PagoServiceAdapter(self._pago_http_client)
        self._campania_service = CampaniaServiceAdapter(self._campania_http_client)
        
        # Casos de uso
        self._dashboard_use_case = None
        self._cliente_detalle_use_case = None
        self._busqueda_integrada_use_case = None
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @property
    def logger_service(self) -> ILoggerService:
        return self._logger_service
    
    @property
    def cache_service(self) -> ICacheService:
        return self._cache_service
    
    @property
    def cliente_service(self) -> IClienteService:
        return self._cliente_service
    
    @property
    def pago_service(self) -> IPagoService:
        return self._pago_service
    
    @property
    def campania_service(self) -> ICampaniaService:
        return self._campania_service
    
    @property
    def dashboard_use_case(self) -> DashboardUseCase:
        if self._dashboard_use_case is None:
            self._dashboard_use_case = DashboardUseCase(
                self.cliente_service,
                self.pago_service,
                self.campania_service,
                self.cache_service,
                self.logger_service
            )
        return self._dashboard_use_case
    
    @property
    def cliente_detalle_use_case(self) -> ClienteDetalleUseCase:
        if self._cliente_detalle_use_case is None:
            self._cliente_detalle_use_case = ClienteDetalleUseCase(
                self.cliente_service,
                self.pago_service,
                self.campania_service,
                self.cache_service,
                self.logger_service
            )
        return self._cliente_detalle_use_case
    
    @property
    def busqueda_integrada_use_case(self) -> BusquedaIntegradaUseCase:
        if self._busqueda_integrada_use_case is None:
            self._busqueda_integrada_use_case = BusquedaIntegradaUseCase(
                self.cliente_service,
                self.pago_service,
                self.campania_service,
                self.logger_service
            )
        return self._busqueda_integrada_use_case
    
    @property
    def validacion_use_case(self) -> ValidacionUseCase:
        return ValidacionUseCase()
    
    async def cleanup(self):
        """Limpia recursos y cierra conexiones"""
        try:
            await self._cliente_http_client.http_client.close()
            await self._pago_http_client.http_client.close()
            await self._campania_http_client.http_client.close()
        except Exception as e:
            logging.error(f"Error cerrando conexiones HTTP: {e}")


# Instancia global del contenedor
container = DIContainer()