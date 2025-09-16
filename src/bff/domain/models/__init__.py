"""
Domain Models para BFF Web UI

Estos modelos representan las entidades específicas para la UI web,
agregando y transformando datos de múltiples servicios backend.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class EstadoCliente(Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"


class EstadoPago(Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"


class EstadoCampania(Enum):
    CREADA = "CREADA"
    APROBADA = "APROBADA"
    CANCELADA = "CANCELADA"


@dataclass
class ClienteWeb:
    """Modelo optimizado para mostrar clientes en UI web"""
    id: str
    nombre: str
    email: str
    cedula: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    estado: EstadoCliente = EstadoCliente.ACTIVO
    total_pagos: int = 0
    monto_total_pagos: Decimal = field(default_factory=lambda: Decimal('0'))
    ultimo_pago: Optional[datetime] = None
    campanias_activas: int = 0


@dataclass
class PagoWeb:
    """Modelo optimizado para mostrar pagos en UI web"""
    id: str
    partner_id: str
    cliente_nombre: Optional[str] = None
    monto: Decimal = field(default_factory=lambda: Decimal('0'))
    moneda: str = "USD"
    estado: EstadoPago = EstadoPago.PENDIENTE
    fecha_creacion: Optional[datetime] = None
    fecha_procesamiento: Optional[datetime] = None
    metodo_pago: Optional[str] = None
    confirmation_id: Optional[str] = None


@dataclass
class CampaniaWeb:
    """Modelo optimizado para mostrar campañas en UI web"""
    id: str
    cliente_id: str
    cliente_nombre: Optional[str] = None
    itinerario: List[str] = field(default_factory=list)
    estado: EstadoCampania = EstadoCampania.CREADA
    fecha_creacion: Optional[datetime] = None
    fecha_aprobacion: Optional[datetime] = None
    pago_asociado_id: Optional[str] = None


@dataclass
class DashboardData:
    """Datos agregados para el dashboard principal"""
    total_clientes: int = 0
    clientes_activos: int = 0
    total_pagos: int = 0
    monto_total_procesado: Decimal = field(default_factory=lambda: Decimal('0'))
    pagos_pendientes: int = 0
    campanias_activas: int = 0
    campanias_completadas: int = 0


@dataclass
class ClienteDetalle:
    """Vista detallada de cliente con datos relacionados"""
    cliente: ClienteWeb
    pagos_recientes: List[PagoWeb] = field(default_factory=list)
    campanias_recientes: List[CampaniaWeb] = field(default_factory=list)
    estadisticas: dict = field(default_factory=dict)


@dataclass
class PaginationInfo:
    """Información de paginación"""
    page: int = 1
    per_page: int = 10
    total_items: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False


@dataclass
class PaginatedResult:
    """Resultado paginado genérico"""
    items: List = field(default_factory=list)
    pagination: PaginationInfo = field(default_factory=PaginationInfo)