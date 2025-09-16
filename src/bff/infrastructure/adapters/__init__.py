"""
Adaptadores de infraestructura para servicios auxiliares
"""

import logging
from typing import Optional, Any
from bff.application.ports import ICacheService, ILoggerService


class InMemoryCacheAdapter(ICacheService):
    """Adaptador de caché en memoria simple"""
    
    def __init__(self):
        self._cache = {}
        self._ttls = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché"""
        if key in self._cache:
            return self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Establece valor en caché"""
        self._cache[key] = value
        # En una implementación real, se manejaría TTL apropiadamente
    
    async def delete(self, key: str) -> None:
        """Elimina valor del caché"""
        self._cache.pop(key, None)
        self._ttls.pop(key, None)
    
    async def clear_pattern(self, pattern: str) -> None:
        """Limpia claves que coincidan con patrón"""
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            await self.delete(key)


class PythonLoggerAdapter(ILoggerService):
    """Adaptador para el sistema de logging estándar de Python"""
    
    def __init__(self, name: str = "bff"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Configurar handler si no existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs) -> None:
        """Log nivel info"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log nivel warning"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log nivel error"""
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log nivel debug"""
        self.logger.debug(message, extra=kwargs)