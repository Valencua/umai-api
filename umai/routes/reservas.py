from flask import Blueprint, jsonify, request

from umai.constants import ERROR_CODE_INVALID_BODY, ERROR_CODES_CONFLICTO
from umai.services.reservas import crear_reserva
from umai.utils import construir_error_api
from umai.validators.reservas import validar_crear_reserva

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/', methods=['POST'])
def post_reserva():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        data = validar_crear_reserva(body)
        reserva = crear_reserva(data)
    except ValueError as e:
        error = e.args[0]
        if error['errors'][0]['code'] in ERROR_CODES_CONFLICTO:
            return jsonify(error), 409
        return jsonify(error), 400

    return jsonify(reserva), 201
