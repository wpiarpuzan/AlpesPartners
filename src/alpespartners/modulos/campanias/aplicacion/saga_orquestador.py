import pulsar
import json
import logging
from pulsar import ConsumerType
from threading import Thread

# Configuración de canales Pulsar
PULSAR_BROKER_URL = 'pulsar://broker:6650'
TOPIC_EVENTOS_CAMPANIAS = 'persistent://public/default/eventos-campanias'
TOPIC_COMANDOS_PAGOS = 'persistent://public/default/comandos-pagos'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos-json'
TOPIC_COMANDOS_CLIENTES = 'persistent://public/default/comandos-clientes'

class SagaOrquestador:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_BROKER_URL)
        self.producer_campanias = self.client.create_producer(TOPIC_EVENTOS_CAMPANIAS)
        self.producer_pagos = self.client.create_producer(TOPIC_COMANDOS_PAGOS)
        self.producer_clientes = self.client.create_producer(TOPIC_COMANDOS_CLIENTES)
        self.consumer_pagos = self.client.subscribe(TOPIC_EVENTOS_PAGOS, subscription_name='saga-campanias', consumer_type=ConsumerType.Shared)

    def iniciar_saga(self, campania_data):
        # Paso 1: Crear campaña usando la lógica real
        from alpespartners.modulos.campanias.aplicacion.dto import CrearCampaniaDTO
        from alpespartners.modulos.campanias.aplicacion.servicio import CampaniasService
        service = CampaniasService()
        cmd = CrearCampaniaDTO(
            idCampania=campania_data['idCampania'],
            idCliente=campania_data['idCliente'],
            itinerario=campania_data['itinerario']
        )
        service.handle_crear_campania(cmd)
        logging.info(f"[SAGA] Campania creada y evento publicado: {campania_data}")
        # Paso 2: Enviar comando para procesar pago usando Pulsar
        comando_pago = {
            'type': 'ProcesarPago',
            'data': {
                'partner_id': campania_data['idCliente'],
                'cycle_id': campania_data.get('cycle_id', 'default_cycle'),
                'monto': campania_data.get('monto', 0),
                'idCampania': campania_data['idCampania']
            }
        }
        self.producer_pagos.send(json.dumps(comando_pago).encode('utf-8'))
        logging.info(f"[SAGA] Comando ProcesarPago enviado: {comando_pago}")
        # Paso 3: Esperar resultado del pago
        Thread(target=self.escuchar_eventos_pago, args=(campania_data,)).start()

    def escuchar_eventos_pago(self, campania_data):
        while True:
            msg = self.consumer_pagos.receive()
            raw = msg.data()
            try:
                evento = json.loads(raw)
            except Exception as e:
                logging.error(f"[CAMPANIAS][SAGA_ORQ] Error parseando evento. Raw: {raw}. Error: {e}")
                consumer.acknowledge(msg)
                continue
            tipo = evento.get('type')
            data = evento.get('data', {})
            if data.get('idCampania') != campania_data['idCampania']:
                self.consumer_pagos.acknowledge(msg)
                continue
            if tipo == 'PagoExitoso':
                self.procesar_pago_exitoso(campania_data, data)
            elif tipo == 'PagoFallido':
                self.procesar_pago_fallido(campania_data, data)
            self.consumer_pagos.acknowledge(msg)
            break

    def procesar_pago_exitoso(self, campania_data, pago_data):
        # Actualizar estado de campaña usando la lógica real
        from alpespartners.modulos.campanias.dominio.entidades import CampaniaAprobada
        from alpespartners.modulos.campanias.infraestructura.event_store import append_event
        from alpespartners.modulos.campanias.infraestructura.publisher import publish_event
        from datetime import datetime
        evento_aprobada = CampaniaAprobada(
            idCampania=campania_data['idCampania'],
            fechaAprobacion=datetime.utcnow()
        )
        append_event(campania_data['idCampania'], "CampaniaAprobada.v1", evento_aprobada.to_dict())
        publish_event("CampaniaAprobada.v1", evento_aprobada.to_dict())
        logging.info(f"[SAGA] CampaniaAprobada publicada y persistida: {campania_data}")
        # Enviar comando para actualizar cliente
        comando_cliente = {'type': 'ActualizarCliente', 'data': {'idCliente': campania_data['idCliente'], 'accion': 'APROBAR_CAMPANIA'}}
        self.producer_clientes.send(json.dumps(comando_cliente).encode('utf-8'))
        logging.info(f"[SAGA] Comando ActualizarCliente enviado: {comando_cliente}")

    def procesar_pago_fallido(self, campania_data, pago_data):
        # Actualizar estado de campaña usando la lógica real
        from alpespartners.modulos.campanias.dominio.entidades import CampaniaCancelada
        from alpespartners.modulos.campanias.infraestructura.event_store import append_event
        from alpespartners.modulos.campanias.infraestructura.publisher import publish_event
        from datetime import datetime
        evento_cancelada = CampaniaCancelada(
            idCampania=campania_data['idCampania'],
            motivo=pago_data.get('reason', 'Pago fallido'),
            fechaCancelacion=datetime.utcnow()
        )
        append_event(campania_data['idCampania'], "CampaniaCancelada.v1", evento_cancelada.__dict__)
        publish_event("CampaniaCancelada.v1", evento_cancelada.__dict__)
        logging.info(f"[SAGA] CampaniaCancelada publicada y persistida: {campania_data}")
        # Enviar comando para actualizar cliente
        comando_cliente = {'type': 'ActualizarCliente', 'data': {'idCliente': campania_data['idCliente'], 'accion': 'CANCELAR_CAMPANIA'}}
        self.producer_clientes.send(json.dumps(comando_cliente).encode('utf-8'))
        logging.info(f"[SAGA] Comando ActualizarCliente enviado: {comando_cliente}")

    def close(self):
        self.client.close()

# Ejemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    saga = SagaOrquestador()
    campania_data = {
        'idCampania': 'camp123',
        'idCliente': 'cli456',
        'itinerario': ['vuelo1', 'vuelo2'],
        'monto': 1000
    }
    saga.iniciar_saga(campania_data)
    # saga.close() # Llamar al finalizar
