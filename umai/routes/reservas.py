from flask import Blueprint, jsonify

from umai.utils import construir_error_api
from umai.services.reservas import traer_3_mas_recientes_reservas

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/', methods=['GET'])
def get_3_reservas():
    try:
        reservas = traer_3_mas_recientes_reservas()
        if(reservas is None):
            return jsonify(construir_error_api('DB_ERROR', 'Error al acceder a la base de datos', 'No se pudieron obtener las reservas')), 500
        return jsonify({'data': reservas, 'status': 'success'}), 200
    
    except Exception:
        return jsonify(construir_error_api('LIST_ERROR', 'Error listando las 3 reservas más recientes', 'Error inesperado')), 500
    