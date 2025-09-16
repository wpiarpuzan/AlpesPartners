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

    import os
    PULSAR_BROKER_URL = os.environ['PULSAR_BROKER_URL']
    client = pulsar.Client(PULSAR_BROKER_URL)
    # Subscribe to the JSON-only topic for client updater to avoid Avro/JSON mixing
    # Use Shared consumer type so multiple consumers can co-exist
    consumer = client.subscribe('persistent://public/default/eventos-pagos-json', subscription_name='cliente-actualizador', consumer_type=pulsar.ConsumerType.Shared)
    print(f"[cliente] Subscrito a eventos-pagos-json (JSON)")

    while True:
        msg = consumer.receive()
        raw = msg.data()
        try:
            evento = _parse_event(raw)
        except Exception as e:
            print(f"[cliente] Error parseando evento. Raw: {raw}. Error: {e}")
            consumer.acknowledge(msg)
            continue
        tipo = evento.get('type')
        data = evento.get('data', {})
        if tipo == 'ActualizarCliente':
            accion = data.get('accion')
            id_cliente = data.get('idCliente')
            from alpespartners.api import create_app
            from alpespartners.modulos.cliente.infraestructura.repositorios import ClienteRepositorioSQLAlchemy
            app = None
            try:
                app = create_app({'TESTING': True})
            except Exception:
                app = None

            # Use a context manager to ensure proper push/pop of the Flask app context
            if app is not None:
                try:
                    with app.app_context():
                        repo = ClienteRepositorioSQLAlchemy()
                        if accion == 'APROBAR_CAMPANIA':
                            # Aquí podrías sumar una campaña aprobada, actualizar estado, etc.
                            # Ejemplo: repo.actualizar_estado(id_cliente, 'APROBADA')
                            pass
                        elif accion == 'CANCELAR_CAMPANIA':
                            # Aquí podrías sumar una campaña cancelada, actualizar estado, etc.
                            # Ejemplo: repo.actualizar_estado(id_cliente, 'CANCELADA')
                            pass
                except Exception as e:
                    print(f"[cliente] Error al ejecutar con app_context: {e}")
            else:
                # Fall back to creating repo without app context (less safe but won't crash)
                try:
                    repo = ClienteRepositorioSQLAlchemy()
                    if accion == 'APROBAR_CAMPANIA':
                        pass
                    elif accion == 'CANCELAR_CAMPANIA':
                        pass
                except Exception as e:
                    print(f"[cliente] Error al ejecutar repositorio sin app_context: {e}")
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