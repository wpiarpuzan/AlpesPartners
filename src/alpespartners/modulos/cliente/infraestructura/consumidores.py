# -*- coding: utf-8 -*-
import os, json, re
from datetime import datetime
from .repositorios import ClienteRepositorioSQLAlchemy
from alpespartners.config.db import db as db_session
from alpespartners.modulos.cliente.infraestructura.dto import ClienteModel as Cliente

try:
    import pulsar
except Exception:
    pulsar = None

PULSAR_ADDR = os.getenv("PULSAR_ADDRESS", "broker")
PAGOS_TOPIC = os.getenv("PAGOS_TOPIC", "persistent://public/default/pagos")

def _parse_event(data: bytes) -> dict:
    raw = data.decode("utf-8")
    try:
        return json.loads(raw)
    except Exception:
        # fallback para dataclass repr tipo "PagoRegistrado(pago_id='...', ...)"
        pairs = re.findall(r"(\w+)=('([^']*)'|([^,()]+))", raw)
        ev = {k: (v2 if v2 else v3) for (k, _, v2, v3) in pairs}
        if "PagoRegistrado" in raw and "type" not in ev:
            ev["type"] = "PagoRegistrado"
        return ev

def suscribirse_a_pagos():
    if pulsar is None:
        print("[cliente] Pulsar no disponible; no se puede consumir eventos.")
        return

    client = pulsar.Client(f"pulsar://{PULSAR_ADDR}:6650")
    consumer = client.subscribe('eventos-pagos', subscription_name='cliente-actualizador')
    print(f"[cliente] Subscrito a {PAGOS_TOPIC}")

    while True:
        msg = consumer.receive()
        evento = json.loads(msg.data())
        tipo = evento.get('type')
        data = evento.get('data', {})
        if tipo == 'ActualizarCliente':
            accion = data.get('accion')
            id_cliente = data.get('idCliente')
            from alpespartners.modulos.cliente.infraestructura.repositorios import ClienteRepositorioSQLAlchemy
            repo = ClienteRepositorioSQLAlchemy()
            if accion == 'APROBAR_CAMPANIA':
                # Aquí podrías sumar una campaña aprobada, actualizar estado, etc.
                # Ejemplo: repo.actualizar_estado(id_cliente, 'APROBADA')
                pass
            elif accion == 'CANCELAR_CAMPANIA':
                # Aquí podrías sumar una campaña cancelada, actualizar estado, etc.
                # Ejemplo: repo.actualizar_estado(id_cliente, 'CANCELADA')
                pass
        consumer.acknowledge(msg)
    client.close()

if __name__ == "__main__":
    suscribirse_a_pagos()


def suscribirse_a_comandos():
    ...