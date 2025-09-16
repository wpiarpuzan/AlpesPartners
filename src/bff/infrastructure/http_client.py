"""
Cliente HTTP para comunicación con microservicios de Alpes Partners                if response.status >= 400:
                    self._handle_error_response(response, response_text)
Este cliente maneja toda la comunicación HTTP con los servicios backend,
incluyendo manejo de errores, timeouts, y logging.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import aiohttp
from aiohttp import ClientTimeout, ClientSession

from bff.domain.exceptions import ServiceUnavailableException, ValidationException


class AlpesPartnersHttpClient:
    """Cliente HTTP para comunicación con servicios Alpes Partners"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = ClientTimeout(total=timeout)
        self.logger = logging.getLogger(__name__)
        self._session: Optional[ClientSession] = None
    
    def _get_session(self) -> ClientSession:
        """Obtiene una sesión HTTP reutilizable"""
        if self._session is None or self._session.closed:
            self._session = ClientSession(
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'BFF-WebUI/1.0.0'
                }
            )
        return self._session
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza una petición GET
        
        Args:
            endpoint: Endpoint relativo (ej: '/cliente/123')
            params: Parámetros de query string
            
        Returns:
            Respuesta JSON deserializada
            
        Raises:
            ServiceUnavailableException: Si el servicio no está disponible
            ValidationException: Si hay error de validación
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        session = self._get_session()
        
        try:
            self.logger.info(f"GET {url} with params: {params}")
            
            async with session.get(url, params=params) as response:
                response_text = await response.text()
                
                self.logger.info(f"Response {response.status}: {response_text[:200]}...")
                
                if response.status == 404:
                    return {}  # Recurso no encontrado
                elif response.status >= 400:
                    await self._handle_error_response(response, response_text)
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Error de conexión en GET {url}: {str(e)}")
            raise ServiceUnavailableException("alpespartners", f"Error de conexión: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decodificando JSON en GET {url}: {str(e)}")
            raise ServiceUnavailableException("alpespartners", "Respuesta inválida del servicio")
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una petición POST
        
        Args:
            endpoint: Endpoint relativo
            data: Datos a enviar en el body
            
        Returns:
            Respuesta JSON deserializada
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        session = self._get_session()
        
        try:
            self.logger.info(f"POST {url} with data: {json.dumps(data, default=str)[:200]}...")
            
            async with session.post(url, json=data) as response:
                response_text = await response.text()
                
                self.logger.info(f"Response {response.status}: {response_text[:200]}...")
                
                if response.status >= 400:
                    self._handle_error_response(response, response_text)
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Error de conexión en POST {url}: {str(e)}")
            raise ServiceUnavailableException("alpespartners", f"Error de conexión: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decodificando JSON en POST {url}: {str(e)}")
            raise ServiceUnavailableException("alpespartners", "Respuesta inválida del servicio")
    
    def _handle_error_response(self, response, response_text: str):
        """Maneja respuestas de error del servicio"""
        try:
            error_data = json.loads(response_text)
            error_message = error_data.get('message', error_data.get('error', 'Error desconocido'))
        except json.JSONDecodeError:
            error_message = f"HTTP {response.status}: {response_text}"
        
        if response.status == 400:
            raise ValidationException(error_message)
        elif response.status >= 500:
            raise ServiceUnavailableException("alpespartners", error_message)
        else:
            raise ServiceUnavailableException("alpespartners", f"HTTP {response.status}: {error_message}")


class ClienteServiceHttpClient:
    """Cliente específico para el servicio de clientes"""
    
    def __init__(self, http_client: AlpesPartnersHttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def obtener_cliente(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por ID"""
        response = await self.http_client.get(f'/cliente/{cliente_id}')
        return response if response else None
    
    async def crear_cliente(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo cliente"""
        return await self.http_client.post('/cliente/registrar', datos)
    
    def listar_clientes(self, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Lista clientes (simulado - el servicio actual no tiene endpoint de listado)
        En producción se implementaría un endpoint específico para listado
        """
        # Usamos los parámetros para evitar warnings
        _ = (page, per_page)
        self.logger.warning("Listado de clientes no implementado en el servicio backend, retornando datos mock")
        # Por ahora retornamos mock data hasta que se implemente el endpoint
        return []


class PagoServiceHttpClient:
    """Cliente específico para el servicio de pagos"""
    
    def __init__(self, http_client: AlpesPartnersHttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def obtener_pago(self, pago_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un pago por ID"""
        response = await self.http_client.get(f'/pagos/{pago_id}')
        return response if response else None
    
    async def crear_pago(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo pago"""
        return await self.http_client.post('/pagos/pagar', datos)
    
    def listar_pagos(self, page: int = 1, per_page: int = 20, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista pagos (simulado - el servicio actual no tiene endpoint de listado)
        En producción se implementaría un endpoint específico para listado
        """
        # Usamos los parámetros para evitar warnings
        _ = (page, per_page, filtros)
        self.logger.warning("Listado de pagos no implementado en el servicio backend, retornando datos mock")
        # Por ahora retornamos mock data hasta que se implemente el endpoint
        return []


class CampaniaServiceHttpClient:
    """Cliente específico para el servicio de campañas"""
    
    def __init__(self, http_client: AlpesPartnersHttpClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
    
    async def obtener_campania(self, campania_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una campaña por ID"""
        response = await self.http_client.get(f'/campanias/{campania_id}')
        return response if response else None
    
    async def crear_campania(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva campaña"""
        return await self.http_client.post('/campanias/comandos/crear', datos)
    
    def listar_campanias(self, page: int = 1, per_page: int = 20, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista campañas (simulado - el servicio actual no tiene endpoint de listado)
        En producción se implementaría un endpoint específico para listado
        """
        # Usamos los parámetros para evitar warnings
        _ = (page, per_page, filtros)
        self.logger.warning("Listado de campañas no implementado en el servicio backend, retornando datos mock")
        # Por ahora retornamos mock data hasta que se implemente el endpoint
        return []


# Factory para crear clientes HTTP
class HttpClientFactory:
    """Factory para crear instancias de clientes HTTP"""
    
    @staticmethod
    def create_alpespartners_client(base_url: str, timeout: int = 30) -> AlpesPartnersHttpClient:
        """Crea cliente HTTP para Alpes Partners"""
        return AlpesPartnersHttpClient(base_url, timeout)
    
    @staticmethod
    def create_cliente_client(base_url: str, timeout: int = 30) -> ClienteServiceHttpClient:
        """Crea cliente HTTP para servicio de clientes"""
        http_client = AlpesPartnersHttpClient(base_url, timeout)
        return ClienteServiceHttpClient(http_client)
    
    @staticmethod
    def create_pago_client(base_url: str, timeout: int = 30) -> PagoServiceHttpClient:
        """Crea cliente HTTP para servicio de pagos"""
        http_client = AlpesPartnersHttpClient(base_url, timeout)
        return PagoServiceHttpClient(http_client)
    
    @staticmethod
    def create_campania_client(base_url: str, timeout: int = 30) -> CampaniaServiceHttpClient:
        """Crea cliente HTTP para servicio de campañas"""
        http_client = AlpesPartnersHttpClient(base_url, timeout)
        return CampaniaServiceHttpClient(http_client)