from flask import Blueprint, jsonify
from umai.services.metricas import obtener_rating_promedio, obtener_cancelaciones_hoy
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