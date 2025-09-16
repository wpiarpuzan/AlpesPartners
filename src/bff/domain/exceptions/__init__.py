"""
Excepciones específicas del dominio BFF
"""


class BFFDomainException(Exception):
    """Excepción base para el dominio BFF"""
    pass


class ClienteNotFoundException(BFFDomainException):
    """Cliente no encontrado"""
    def __init__(self, cliente_id: str):
        super().__init__(f"Cliente con ID {cliente_id} no encontrado")
        self.cliente_id = cliente_id


class PagoNotFoundException(BFFDomainException):
    """Pago no encontrado"""
    def __init__(self, pago_id: str):
        super().__init__(f"Pago con ID {pago_id} no encontrado")
        self.pago_id = pago_id


class CampaniaNotFoundException(BFFDomainException):
    """Campaña no encontrada"""
    def __init__(self, campania_id: str):
        super().__init__(f"Campaña con ID {campania_id} no encontrada")
        self.campania_id = campania_id


class ServiceUnavailableException(BFFDomainException):
    """Servicio backend no disponible"""
    def __init__(self, service_name: str, detail: str = ""):
        message = f"Servicio {service_name} no disponible"
        if detail:
            message += f": {detail}"
        super().__init__(message)
        self.service_name = service_name
        self.detail = detail


class ValidationException(BFFDomainException):
    """Error de validación de datos"""
    def __init__(self, field: str, message: str):
        super().__init__(f"Error de validación en campo '{field}': {message}")
        self.field = field


class PaginationException(BFFDomainException):
    """Error en parámetros de paginación"""
    pass