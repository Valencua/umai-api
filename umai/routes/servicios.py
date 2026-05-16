from flask import Blueprint, jsonify, request

from umai.validators.servicios import validar_crear_servicio
from umai.utils import construir_error_api
from umai.services.servicios import crear_servicio

from ..constants import (
    ERROR_CODE_INVALID_BODY)

servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/', methods=['POST'])
def post_servicio():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        data = validar_crear_servicio(body)
        servicio = crear_servicio(data)
    except ValueError as e:
        return jsonify(e.args[0]), 400
    
    return jsonify(servicio), 201