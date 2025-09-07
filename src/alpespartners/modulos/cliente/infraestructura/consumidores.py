# -*- coding: utf-8 -*-
import os, json, re
from datetime import datetime
from .repositorios import ClienteRepositorioSQLAlchemy

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
    consumer = client.subscribe(PAGOS_TOPIC, subscription_name="cliente-proyeccion")
    print(f"[cliente] Subscrito a {PAGOS_TOPIC}")

    repo = ClienteRepositorioSQLAlchemy()

    while True:
        msg = consumer.receive()
        try:
            ev = _parse_event(msg.data())
            if ev.get("type") in ("PagoRegistrado", "alpespartners.pagos.PagoRegistrado", None):
                cliente_id = ev.get("cliente_id")
                fecha = ev.get("fecha")
                if isinstance(fecha, str):
                    try:
                        fecha = datetime.fromisoformat(fecha)
                    except Exception:
                        fecha = None
                repo.actualizar_totales_por_pago(cliente_id, fecha or datetime.utcnow())
            consumer.acknowledge(msg)
        except Exception as e:
            print("[cliente] error procesando evento:", e)
            consumer.negative_acknowledge(msg)

if __name__ == "__main__":
    suscribirse_a_pagos()


def suscribirse_a_comandos():
    ...