from dataclasses import dataclass
import uuid
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartners.seedwork.aplicacion.comandos import Comando, ComandoHandler
from cliente.dominio.entidades import ClienteNatural
from cliente.dominio.objetos_valor import Email, Cedula
from cliente.dominio.repositorios import IClienteRepositorio
from cliente.infraestructura.fabricas import FabricaRepositorio
from alpespartners.seedwork.infraestructura.uow import UnidadTrabajoPuerto
from datetime import datetime


@dataclass
class RegistrarCliente(Comando):
    id: str
    nombre: str
    email: str
    cedula: str
    fecha_nacimiento: str  # ISO format


class RegistrarClienteHandler(ComandoHandler):
    def handle(self, comando: RegistrarCliente):
        fabrica = FabricaRepositorio()
        repo: IClienteRepositorio = fabrica.crear_objeto(IClienteRepositorio)

        email_str = comando.email
        address = email_str
        dominio = email_str.split('@')[1] if '@' in email_str else ''
        es_empresarial = dominio.endswith('.com') or dominio.endswith('.org')

        email = Email(address, dominio, es_empresarial)
        cliente = ClienteNatural(
            nombre=comando.nombre,
            email=email,
            cedula=Cedula(comando.cedula),
            fecha_nacimiento=datetime.fromisoformat(comando.fecha_nacimiento),
            fecha_registro=datetime.now(),
            total_pagos=0
        )
        cliente._id = uuid.UUID(comando.id)
        
        UnidadTrabajoPuerto.registrar_batch(repo.agregar, cliente)
        UnidadTrabajoPuerto.savepoint()
        UnidadTrabajoPuerto.commit()
        return cliente


@comando.register(RegistrarCliente)
def ejecutar_comando_registrar_cliente(comando: RegistrarCliente):
    handler = RegistrarClienteHandler()
    return handler.handle(comando)
