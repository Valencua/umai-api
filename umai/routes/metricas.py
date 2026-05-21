from flask import Blueprint, jsonify
from umai.services.metricas import obtener_dashboard
from umai.utils import construir_error_api
from umai.constants import ERROR_CODE_INTERNAL_SERVER

metricas_bp = Blueprint('metricas', __name__)

@metricas_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    try:
        dashboard = obtener_dashboard()
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al obtener el dashboard',
            description='Ocurrió un error interno'
        )), 500

    return jsonify(dashboard), 200