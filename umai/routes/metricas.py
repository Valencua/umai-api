
from flask import Blueprint, jsonify

from umai.constants import ERROR_CODE_INTERNAL_SERVER
from umai.services.metricas import obtener_reservas_hoy as obtener_reservas_hoy_service
from umai.utils import construir_error_api

metricas_bp = Blueprint('metricas', __name__)

@metricas_bp.route('/reservas-hoy', methods=['GET'])
def obtener_reservas_hoy():
    try:
        reservas = obtener_reservas_hoy_service()

        if reservas is None:
            return jsonify(construir_error_api(
                code=ERROR_CODE_INTERNAL_SERVER,
                message='Error al obtener reservas',
                description='Ocurrió un error al intentar obtener las reservas para hoy'
            )), 500

        return jsonify({
            'data': reservas,
            'status': 'success'
        }), 200
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al obtener reservas',
            description='Ocurrió un error al intentar obtener las reservas para hoy'
        )), 500



