from flask import Blueprint, jsonify

from umai.utils import construir_error_api
from umai.services.reservas import get_top3_reservas
from umai.constants import ERROR_CODE_INTERNAL_SERVER

reservas_bp = Blueprint('reservas', __name__)

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
    