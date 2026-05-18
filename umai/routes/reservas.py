from flask import Blueprint, jsonify, request

from umai.constants import ERROR_CODE_INTERNAL_SERVER
from umai.services.reservas import obtener_disponibilidad
from umai.utils import construir_error_api

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

@reservas_bp.route('/disponibilidad', methods=['GET'])
def get_disponibilidad():
    
    fecha = request.args.get('fecha')

    if not fecha:

        return jsonify(construir_error_api(
            code='required.fecha',
            message='Fecha requerida',
            description='Debe enviar la fecha en formato YYYY-MM-DD'
        )), 400

    try:
        disponibilidad = obtener_disponibilidad(fecha)
        return jsonify({
            'data': disponibilidad,
            'status': 'success'
        }), 200
    
    except ValueError as e:

        return jsonify(e.args[0]), 400
    
    except Exception:

        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error obteniendo disponibilidad',
            description='Ocurrió un error inesperado'
        )), 500