from flask import Blueprint, jsonify
from umai.services.metricas import obtener_rating_promedio, obtener_reservas_semanal
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