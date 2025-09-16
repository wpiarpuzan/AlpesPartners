# Endpoint para consultar campaña por id
@bff_bp.route('/campanias/<id_campania>', methods=['GET'])
@async_route
async def get_campania(id_campania):
    """Consulta el estado de una campaña por id"""
    import os, requests
    backend_url = os.environ['ALPESPARTNERS_SERVICE_URL']
    try:
        resp = requests.get(f"{backend_url}/campanias/{id_campania}", timeout=10)
        if resp.status_code == 404:
            return jsonify({'error': 'Campania no encontrada'}), 404
        if resp.status_code != 200:
            return jsonify({'error': 'Error consultando campaña', 'backend_status': resp.status_code, 'backend_response': resp.text}), 502
        data = resp.json().get('campania')
        if not data:
            return jsonify({'error': 'Campania no encontrada'}), 404
        # Mapear estados y mensajes
        estado = data.get('estado', 'PENDIENTE')
        msg = 'En proceso'
        if estado == 'APROBADA':
            msg = 'Campaña aprobada'
        elif estado == 'CANCELADA':
            msg = 'Campaña cancelada'
        return jsonify({'idCampania': id_campania, 'estado': estado, 'mensaje': msg, 'detalle': data}), 200
    except Exception as e:
        current_app.logger.error(f"Error consultando campaña en backend: {e}")
        return jsonify({'error': 'Timeout o error de red al consultar campaña', 'details': str(e)}), 504
# Endpoint para crear campaña (flujo principal Saga)
@bff_bp.route('/campanias', methods=['POST'])
@async_route
async def crear_campania():
    """Crea una campaña y dispara la saga (coreografía)"""
    try:
        schema = CampaniaCreateSchema()
        data = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400

    # Generar idCampania único si no viene
    import uuid
    id_campania = data.get('idCampania') or str(uuid.uuid4())
    payload = {
        'idCampania': id_campania,
        'idCliente': data['cliente_id'],
        'itinerario': data['itinerario']
    }
    # Llamar backend AlpesPartners (comando crear campaña)
    import os, requests
    backend_url = os.environ['ALPESPARTNERS_SERVICE_URL']
    try:
        resp = requests.post(f"{backend_url}/campanias/comandos/crear", json=payload, timeout=10)
        if resp.status_code not in (200, 201, 202):
            return jsonify({'error': 'Error creando campaña', 'backend_status': resp.status_code, 'backend_response': resp.text}), 502
    except Exception as e:
        current_app.logger.error(f"Error llamando a backend AlpesPartners: {e}")
        return jsonify({'error': 'Timeout o error de red al crear campaña', 'details': str(e)}), 504

    current_app.logger.info(f"Campaña creada: {id_campania}")
    return jsonify({'idCampania': id_campania, 'status': 'PENDIENTE'}), 202
"""
Controladores web para el BFF

Implementa los endpoints REST optimizados para interfaces web,
siguiendo principios RESTful y mejores prácticas de API design.
"""

import asyncio
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError

from bff.infrastructure.config import container
from bff.domain.models import PaginationInfo
from bff.domain.exceptions import (
    BFFDomainException, ClienteNotFoundException, PagoNotFoundException,
    CampaniaNotFoundException, ValidationException, PaginationException
)


def async_route(f):
    """Decorador para manejo de funciones asíncronas en Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


# Esquemas de validación con Marshmallow
class PaginationSchema(Schema):
    page = fields.Integer(load_default=1, validate=lambda x: x >= 1)
    per_page = fields.Integer(load_default=10, validate=lambda x: 1 <= x <= 100)


class ClienteCreateSchema(Schema):
    nombre = fields.String(required=True, validate=lambda x: len(x.strip()) >= 2)
    email = fields.Email(required=True)
    cedula = fields.String(required=True, validate=lambda x: len(x.strip()) >= 5)
    fecha_nacimiento = fields.String(required=True)


class PagoCreateSchema(Schema):
    partner_id = fields.String(required=True)
    monto = fields.Decimal(required=True, validate=lambda x: x > 0)
    moneda = fields.String(load_default="USD")
    metodo_pago = fields.String(load_default="CREDIT_CARD")


class CampaniaCreateSchema(Schema):
    cliente_id = fields.String(required=True)
    itinerario = fields.List(fields.String(), required=True, validate=lambda x: len(x) >= 1)


# Blueprint principal del BFF
bff_bp = Blueprint('bff', __name__, url_prefix='/api/v1')


@bff_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Maneja errores de validación de Marshmallow"""
    return jsonify({
        'error': 'Validation Error',
        'message': 'Datos de entrada inválidos',
        'details': error.messages
    }), 400


@bff_bp.errorhandler(BFFDomainException)
def handle_domain_exception(error):
    """Maneja excepciones del dominio BFF"""
    status_code = 404 if isinstance(error, (ClienteNotFoundException, PagoNotFoundException, CampaniaNotFoundException)) else 400
    return jsonify({
        'error': type(error).__name__,
        'message': str(error)
    }), status_code


@bff_bp.errorhandler(Exception)
def handle_generic_exception(error):
    """Maneja excepciones genéricas"""
    current_app.logger.error(f"Error no manejado: {str(error)}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'Ha ocurrido un error interno'
    }), 500


# ============================================================================
# ENDPOINTS DEL DASHBOARD
# ============================================================================

@bff_bp.route('/dashboard', methods=['GET'])
@async_route
async def get_dashboard():
    """
    Obtiene datos agregados para el dashboard principal
    ---
    responses:
        200:
        description: Datos del dashboard
    """
    dashboard_data = await container.dashboard_use_case.obtener_datos_dashboard()
    
    return jsonify({
        'total_clientes': dashboard_data.total_clientes,
        'clientes_activos': dashboard_data.clientes_activos,
        'total_pagos': dashboard_data.total_pagos,
        'monto_total_procesado': float(dashboard_data.monto_total_procesado),
        'pagos_pendientes': dashboard_data.pagos_pendientes,
        'campanias_activas': dashboard_data.campanias_activas,
        'campanias_completadas': dashboard_data.campanias_completadas
    }), 200


# ============================================================================
# ENDPOINTS DE CLIENTES
# ============================================================================

@bff_bp.route('/clientes', methods=['GET'])
@async_route
async def list_clientes():
    """
    Lista clientes con paginación y filtros
    ---
    parameters:
        - name: page
            in: query
            type: integer
            default: 1
        - name: per_page
            in: query
            type: integer
            default: 10
        - name: search
            in: query
            type: string
    """
    # Validar parámetros
    schema = PaginationSchema()
    try:
        params = schema.load(request.args)
    except ValidationError as e:
        return jsonify({'error': 'Parámetros inválidos', 'details': e.messages}), 400
    
    pagination = PaginationInfo(page=params['page'], per_page=params['per_page'])
    search_term = request.args.get('search', '').strip()
    
    if search_term:
        result = await container.cliente_service.buscar_clientes(search_term, pagination)
    else:
        result = await container.cliente_service.listar_clientes(pagination)
    
    return jsonify({
        'items': [
            {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'email': cliente.email,
                'cedula': cliente.cedula,
                'fecha_registro': cliente.fecha_registro.isoformat() if cliente.fecha_registro else None,
                'estado': cliente.estado.value,
                'total_pagos': cliente.total_pagos,
                'monto_total_pagos': float(cliente.monto_total_pagos),
                'campanias_activas': cliente.campanias_activas
            }
            for cliente in result.items
        ],
        'pagination': {
            'page': result.pagination.page,
            'per_page': result.pagination.per_page,
            'total_items': result.pagination.total_items,
            'total_pages': result.pagination.total_pages,
            'has_next': result.pagination.has_next,
            'has_prev': result.pagination.has_prev
        }
    }), 200


@bff_bp.route('/clientes/<cliente_id>', methods=['GET'])
@async_route
async def get_cliente_detalle(cliente_id):
    """
    Obtiene vista detallada de un cliente
    ---
    parameters:
        - name: cliente_id
            in: path
            type: string
            required: true
    """
    detalle = await container.cliente_detalle_use_case.obtener_detalle_cliente(cliente_id)
    
    return jsonify({
        'cliente': {
            'id': detalle.cliente.id,
            'nombre': detalle.cliente.nombre,
            'email': detalle.cliente.email,
            'cedula': detalle.cliente.cedula,
            'fecha_registro': detalle.cliente.fecha_registro.isoformat() if detalle.cliente.fecha_registro else None,
            'estado': detalle.cliente.estado.value,
            'total_pagos': detalle.cliente.total_pagos,
            'campanias_activas': detalle.cliente.campanias_activas
        },
        'pagos_recientes': [
            {
                'id': pago.id,
                'monto': float(pago.monto),
                'moneda': pago.moneda,
                'estado': pago.estado.value,
                'fecha_creacion': pago.fecha_creacion.isoformat() if pago.fecha_creacion else None
            }
            for pago in detalle.pagos_recientes
        ],
        'campanias_recientes': [
            {
                'id': campania.id,
                'itinerario': campania.itinerario,
                'estado': campania.estado.value,
                'fecha_creacion': campania.fecha_creacion.isoformat() if campania.fecha_creacion else None
            }
            for campania in detalle.campanias_recientes
        ],
        'estadisticas': detalle.estadisticas
    }), 200


@bff_bp.route('/clientes', methods=['POST'])
@async_route
async def create_cliente():
    """
    Crea un nuevo cliente
    ---
    parameters:
        - name: body
            in: body
            required: true
            schema:
            type: object
            properties:
                nombre:
                type: string
                email:
                type: string
                cedula:
                type: string
                fecha_nacimiento:
                type: string
    """
    schema = ClienteCreateSchema()
    try:
        datos = schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    
    cliente = await container.cliente_service.crear_cliente(datos)
    
    return jsonify({
        'id': cliente.id,
        'nombre': cliente.nombre,
        'email': cliente.email,
        'cedula': cliente.cedula,
        'mensaje': 'Cliente creado exitosamente'
    }), 201


# ============================================================================
# ENDPOINTS DE PAGOS
# ============================================================================

@bff_bp.route('/pagos', methods=['GET'])
@async_route
async def list_pagos():
    """Lista pagos con paginación y filtros"""
    schema = PaginationSchema()
    try:
        params = schema.load(request.args)
    except ValidationError as e:
        return jsonify({'error': 'Parámetros inválidos', 'details': e.messages}), 400
    
    pagination = PaginationInfo(page=params['page'], per_page=params['per_page'])
    
    # Filtros opcionales
    filtros = {}
    if 'estado' in request.args:
        filtros['estado'] = request.args['estado']
    if 'partner_id' in request.args:
        filtros['partner_id'] = request.args['partner_id']
    
    result = await container.pago_service.listar_pagos(pagination, filtros)
    
    return jsonify({
        'items': [
            {
                'id': pago.id,
                'partner_id': pago.partner_id,
                'cliente_nombre': pago.cliente_nombre,
                'monto': float(pago.monto),
                'moneda': pago.moneda,
                'estado': pago.estado.value,
                'fecha_creacion': pago.fecha_creacion.isoformat() if pago.fecha_creacion else None,
                'metodo_pago': pago.metodo_pago,
                'confirmation_id': pago.confirmation_id
            }
            for pago in result.items
        ],
        'pagination': {
            'page': result.pagination.page,
            'per_page': result.pagination.per_page,
            'total_items': result.pagination.total_items,
            'total_pages': result.pagination.total_pages,
            'has_next': result.pagination.has_next,
            'has_prev': result.pagination.has_prev
        }
    }), 200


@bff_bp.route('/pagos/<pago_id>', methods=['GET'])
@async_route
async def get_pago(pago_id):
    """Obtiene un pago específico"""
    pago = await container.pago_service.obtener_pago(pago_id)
    
    if not pago:
        raise PagoNotFoundException(pago_id)
    
    return jsonify({
        'id': pago.id,
        'partner_id': pago.partner_id,
        'cliente_nombre': pago.cliente_nombre,
        'monto': float(pago.monto),
        'moneda': pago.moneda,
        'estado': pago.estado.value,
        'fecha_creacion': pago.fecha_creacion.isoformat() if pago.fecha_creacion else None,
        'fecha_procesamiento': pago.fecha_procesamiento.isoformat() if pago.fecha_procesamiento else None,
        'metodo_pago': pago.metodo_pago,
        'confirmation_id': pago.confirmation_id
    }), 200


# ============================================================================
# ENDPOINTS DE CAMPAÑAS
# ============================================================================

@bff_bp.route('/campanias', methods=['GET'])
@async_route
async def list_campanias():
    """Lista campañas con paginación y filtros"""
    schema = PaginationSchema()
    try:
        params = schema.load(request.args)
    except ValidationError as e:
        return jsonify({'error': 'Parámetros inválidos', 'details': e.messages}), 400
    
    pagination = PaginationInfo(page=params['page'], per_page=params['per_page'])
    
    # Filtros opcionales
    filtros = {}
    if 'estado' in request.args:
        filtros['estado'] = request.args['estado']
    if 'cliente_id' in request.args:
        filtros['cliente_id'] = request.args['cliente_id']
    
    result = await container.campania_service.listar_campanias(pagination, filtros)
    
    return jsonify({
        'items': [
            {
                'id': campania.id,
                'cliente_id': campania.cliente_id,
                'cliente_nombre': campania.cliente_nombre,
                'itinerario': campania.itinerario,
                'estado': campania.estado.value,
                'fecha_creacion': campania.fecha_creacion.isoformat() if campania.fecha_creacion else None,
                'pago_asociado_id': campania.pago_asociado_id
            }
            for campania in result.items
        ],
        'pagination': {
            'page': result.pagination.page,
            'per_page': result.pagination.per_page,
            'total_items': result.pagination.total_items,
            'total_pages': result.pagination.total_pages,
            'has_next': result.pagination.has_next,
            'has_prev': result.pagination.has_prev
        }
    }), 200


# ============================================================================
# ENDPOINTS DE BÚSQUEDA
# ============================================================================

@bff_bp.route('/search', methods=['GET'])
@async_route
async def search_global():
    """
    Búsqueda integrada en múltiples servicios
    ---
        parameters:
        - name: q
            in: query
            type: string
            required: true
        - name: types
            in: query
            type: string
            description: "Tipos separados por coma: clientes,pagos,campanias"
    """
    termino = request.args.get('q', '').strip()
    if not termino:
        return jsonify({'error': 'Parámetro de búsqueda "q" es requerido'}), 400
    
    tipos_param = request.args.get('types', 'clientes,pagos,campanias')
    tipos = [t.strip() for t in tipos_param.split(',') if t.strip()]
    
    schema = PaginationSchema()
    try:
        params = schema.load(request.args)
    except ValidationError as e:
        return jsonify({'error': 'Parámetros inválidos', 'details': e.messages}), 400
    
    pagination = PaginationInfo(page=params['page'], per_page=params['per_page'])
    
    resultado = await container.busqueda_integrada_use_case.buscar_global(
        termino, tipos, pagination
    )
    
    return jsonify(resultado), 200


# ============================================================================
# HEALTH CHECK
# ============================================================================

@bff_bp.route('/health', methods=['GET'])
def health_check():
    """Health check del BFF"""
    return jsonify({
        'status': 'healthy',
        'service': 'bff-web-ui',
        'version': '1.0.0'
    }), 200