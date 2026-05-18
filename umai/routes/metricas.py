from flask import Blueprint, jsonify

from umai.constants import ERROR_CODE_INTERNAL_SERVER
from umai.services.metricas import obtener_personas_hoy as obtener_personas_hoy_service
from umai.utils import construir_error_api

metricas_bp = Blueprint('metricas', __name__)

@metricas_bp.route('/personas-hoy', methods=['GET'])
def obtener_personas_hoy():
    try:
        personas = obtener_personas_hoy_service()
        if personas is None:
            return jsonify(construir_error_api(
                code=ERROR_CODE_INTERNAL_SERVER,
                message='Error al obtener personas',
                description='Ocurrió un error al intentar obtener las personas para hoy'
            )), 500

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
