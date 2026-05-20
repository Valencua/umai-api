from flask import Blueprint, jsonify
from umai.services.metricas import obtener_rating_promedio, obtener_reservas_hoy, obtener_cancelaciones_hoy, obtener_metricas_reservas, obtener_personas_hoy
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
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al obtener reservas',
            description='Ocurrió un error al intentar obtener las reservas para hoy'
        )), 500
    return jsonify(reservas_cantidad), 200


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
        personas_cantidad = obtener_personas_hoy()
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al obtener personas',
            description='Ocurrió un error al intentar obtener las personas para hoy'
        )), 500
    return jsonify(personas_cantidad), 200


