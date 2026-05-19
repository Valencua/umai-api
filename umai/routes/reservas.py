from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api
from umai.constants import ERROR_CODE_INTERNAL_SERVER
from umai.services.reservas import obtener_reservas

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/', methods=['POST'])
def post_reserva():
    """
    Acá tenemos que recibir 201 si es creada
    400 BAD REQUEST si faltan campos, fecha pasada, horario no disponible
    409 si turno lleno
    Primero validar los datos (aca todo con validators)
    Despues validar fecha
    Luego validar horario
    Si todo corre bien, crear reserva en el service
    """
    return jsonify(), 201


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
    