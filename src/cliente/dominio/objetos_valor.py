from dataclasses import dataclass


@dataclass(frozen=True)
class Nombre:
    nombres: str = ''
    apellidos: str = ''


@dataclass(frozen=True)
class Email:
    address: str = ''
    dominio: str = ''
    es_empresarial: bool = False


@dataclass(frozen=True)
class Cedula:
    numero: int = 0


@dataclass(frozen=True)
class Rut:
    numero: int = 0
    ciudad: str = ''


class MetodosPago:
    ...
