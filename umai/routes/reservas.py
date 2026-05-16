from flask import Blueprint, jsonify, request

from umai.utils import construir_error_api
from umai.validators.reservas import validar_crear_reserva
#from umai.services.reservas import crear_reserva

from umai.constants import ERROR_CODE_INVALID_BODY

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
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400
    try:
        data = validar_crear_reserva(body)
        #reserva = crear_reserva(body)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    return jsonify(data), 201