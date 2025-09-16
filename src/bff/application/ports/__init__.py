"""
Puertos (Interfaces) para la comunicación con servicios backend

Estos puertos definen los contratos para la comunicación con los servicios
de Alpes Partners, siguiendo el principio de inversión de dependencias.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from bff.domain.models import (
    ClienteWeb, PagoWeb, CampaniaWeb, DashboardData,
    ClienteDetalle, PaginatedResult, PaginationInfo
)


class IClienteService(ABC):
    """Puerto para el servicio de clientes"""
    
    @abstractmethod
    async def obtener_cliente(self, cliente_id: str) -> Optional[ClienteWeb]:
        """Obtiene un cliente por ID"""
        pass
    
    @abstractmethod
    async def listar_clientes(self, pagination: PaginationInfo) -> PaginatedResult:
        """Lista clientes con paginación"""
        pass
    
    @abstractmethod
    async def crear_cliente(self, datos: Dict[str, Any]) -> ClienteWeb:
        """Crea un nuevo cliente"""
        pass
    
    @abstractmethod
    async def buscar_clientes(self, termino: str, pagination: PaginationInfo) -> PaginatedResult:
        """Busca clientes por término"""
        pass
    
    @abstractmethod
    async def obtener_estadisticas_cliente(self, cliente_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas específicas del cliente"""
        pass


class IPagoService(ABC):
    """Puerto para el servicio de pagos"""
    
    @abstractmethod
    async def obtener_pago(self, pago_id: str) -> Optional[PagoWeb]:
        """Obtiene un pago por ID"""
        pass
    
    @abstractmethod
    async def listar_pagos(self, pagination: PaginationInfo, filtros: Dict[str, Any] = None) -> PaginatedResult:
        """Lista pagos con filtros y paginación"""
        pass
    
    @abstractmethod
    async def crear_pago(self, datos: Dict[str, Any]) -> PagoWeb:
        """Crea un nuevo pago"""
        pass
    
    @abstractmethod
    async def obtener_pagos_por_cliente(self, cliente_id: str, limit: int = 10) -> List[PagoWeb]:
        """Obtiene pagos recientes de un cliente"""
        pass
    
    @abstractmethod
    async def obtener_estadisticas_pagos(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales de pagos"""
        pass


class ICampaniaService(ABC):
    """Puerto para el servicio de campañas"""
    
    @abstractmethod
    async def obtener_campania(self, campania_id: str) -> Optional[CampaniaWeb]:
        """Obtiene una campaña por ID"""
        pass
    
    @abstractmethod
    async def listar_campanias(self, pagination: PaginationInfo, filtros: Dict[str, Any] = None) -> PaginatedResult:
        """Lista campañas con filtros y paginación"""
        pass
    
    @abstractmethod
    async def crear_campania(self, datos: Dict[str, Any]) -> CampaniaWeb:
        """Crea una nueva campaña"""
        pass
    
    @abstractmethod
    async def obtener_campanias_por_cliente(self, cliente_id: str, limit: int = 10) -> List[CampaniaWeb]:
        """Obtiene campañas de un cliente"""
        pass
    
    @abstractmethod
    async def obtener_estadisticas_campanias(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales de campañas"""
        pass


class ICacheService(ABC):
    """Puerto para el servicio de caché"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Establece valor en caché con TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Elimina valor del caché"""
        pass
    
    @abstractmethod
    async def clear_pattern(self, pattern: str) -> None:
        """Limpia claves que coincidan con patrón"""
        pass


class ILoggerService(ABC):
    """Puerto para el servicio de logging"""
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log nivel info"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log nivel warning"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log nivel error"""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log nivel debug"""
        pass