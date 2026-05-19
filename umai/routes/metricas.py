from flask import Blueprint, jsonify
from umai.services.metricas import obtener_rating_promedio, obtener_reservas_hoy, obtener_cancelaciones_hoy, obtener_metricas_reservas, obtener_personas_hoy, obtener_reservas_semanal
from umai.utils import construir_error_api
from umai.constants import ERROR_CODE_INTERNAL_SERVER

metricas_bp = Blueprint('metricas', __name__)

@metricas_bp.route('/rating', methods=['GET'])
def get_rating_promedio():
    try:
        metricas = obtener_rating_promedio()
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500
    return jsonify(metricas), 200


@metricas_bp.route('/reservas-hoy', methods=['GET'])
def get_reservas_hoy():
    try:
        reservas_cantidad = obtener_reservas_hoy()
        if reservas_cantidad is None:
            return jsonify({
                'data': 0,
                'message': 'No hay reservas para hoy',
                'status': 'success'
            }), 200

        return jsonify({
            'data': reservas_cantidad,
            'status': 'success'
        }), 200
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al obtener reservas',
            description='Ocurrió un error al intentar obtener las reservas para hoy'
        )), 500

@metricas_bp.route('/cancelaciones-hoy', methods=['GET'])
def get_cancelaciones_hoy():
    try:
        cancelaciones = obtener_cancelaciones_hoy()
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500
    return jsonify(cancelaciones), 200

@metricas_bp.route('/reservas', methods=['GET'])
def get_metricas_reservas():
    try:
        metricas = obtener_metricas_reservas()
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500
        
    return jsonify(metricas), 200

@metricas_bp.route('/personas-hoy', methods=['GET'])
def get_personas_hoy():
    try:
        personas = obtener_personas_hoy()
        return jsonify({
            'data': personas,
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al obtener personas',
            description='Ocurrió un error al intentar obtener las personas para hoy'
        )), 500


@metricas_bp.route('/reservas-semanal', methods=['GET'])
def get_reservas_semanal():
    try:
        reservas = obtener_reservas_semanal() 
    except Exception as e:

        import traceback
        traceback.print_exc()
        
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500

    return jsonify({'data': reservas, 'status': 'success'}), 200

