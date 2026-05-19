from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api
from umai.constants import ERROR_CODE_INVALID_BODY, ERROR_CODES_CONFLICTO, ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_RESERVA_NO_ENCONTRADA
from umai.services.reservas import crear_reserva, confirmar_asistencia_por_codigo, get_top3_reservas, obtener_reservas, obtener_reservas_codigo
from umai.utils import construir_error_api
from umai.validators.reservas import validar_crear_reserva, validar_uuid_codigo

from umai.constants import ERROR_CODE_INTERNAL_SERVER
from umai.services.reservas import obtener_disponibilidad
from umai.utils import construir_error_api

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/', methods=['POST'])
def post_reserva():

    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        data = validar_crear_reserva(body)
        reserva = crear_reserva(data)
        return jsonify(reserva), 201
    except ValueError as e:
        error = e.args[0]
        if error['errors'][0]['code'] in ERROR_CODES_CONFLICTO:
            return jsonify(error), 409
        return jsonify(error), 400
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500


@reservas_bp.route('/codigo/<uuid_codigo>', methods=['PATCH'])
def patch_confirmar_asistencia(uuid_codigo):
    try:
        codigo = validar_uuid_codigo(uuid_codigo)
        reserva = confirmar_asistencia_por_codigo(codigo)
        return jsonify(reserva), 200
    except ValueError as e:
        error = e.args[0]
        codigo_error = error['errors'][0]['code']
        if codigo_error == ERROR_CODE_RESERVA_NO_ENCONTRADA:
            return jsonify(error), 404
        if codigo_error in ERROR_CODES_CONFLICTO:
            return jsonify(error), 409
        return jsonify(error), 400
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500

@reservas_bp.route('/reservas-historial', methods=['GET'])
def get_reservas():
    try:
        reservas = obtener_reservas()
        if(reservas is None):
            return jsonify(construir_error_api(
                code='not_found.reservas.empty',
                message="No se encontraron reservas",
                description="No existen reservas registradas en la base de datos actualmente."
            )), 404
        return jsonify(
            {
                'data': reservas, 
                'status': 'success'}
            ), 200
    
    except Exception:
        return jsonify(construir_error_api(
            ERROR_CODE_INTERNAL_SERVER, 
            'Error listando las reservas', 
            'Error inesperado')
        ), 500
    
@reservas_bp.route('/recientes', methods=['GET'])
def get_3_reservas():
    try:
        reservas = get_top3_reservas()
        if(reservas is None):
            return jsonify(construir_error_api(
                ERROR_CODE_INTERNAL_SERVER, 
                'Error al acceder a la base de datos', 
                'No se pudieron obtener las reservas')
            ), 500

        return jsonify(
            {
                'data': reservas, 
                'status': 'success'}
            ), 200
            
    except Exception:
        return jsonify(construir_error_api(
            ERROR_CODE_INTERNAL_SERVER, 
            'Error listando las 3 reservas más recientes', 
            'Error inesperado')
        ), 500

@reservas_bp.route('/reservas/codigo/<string:uuid_codigo>', methods=['GET'])
def obtener_reserva(uuid_codigo):
    reserva = obtener_reservas_codigo(uuid_codigo)

    if reserva:
        return jsonify(reserva), 200
    else:
        return jsonify({"error": "No existe el código de reserva"}), 404

@reservas_bp.route('/disponibilidad', methods=['GET'])
def get_disponibilidad():
    
    fecha = request.args.get('fecha')

    if not fecha:

        return jsonify(construir_error_api(
            code='required.fecha',
            message='Fecha requerida',
            description='Debe enviar la fecha en formato YYYY-MM-DD'
        )), 400

    try:
        disponibilidad = obtener_disponibilidad(fecha)
        return jsonify({
            'data': disponibilidad,
            'status': 'success'
        }), 200
    
    except ValueError as e:

        return jsonify(e.args[0]), 400
    
    except Exception:

        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error obteniendo disponibilidad',
            description='Ocurrió un error inesperado'
        )), 500

