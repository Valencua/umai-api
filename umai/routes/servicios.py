from flask import Blueprint, jsonify, request

from umai.utils import construir_error_api
from umai.services.servicios import actualizar_estado_servicio
from ..constants import ERROR_CODE_INVALID_BODY

servicios_bp = Blueprint('servicios', __name__)


@servicios_bp.route('/<int:servicio_id>/', methods=['PATCH'])
def patch_estado_servicio(servicio_id):
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        servicio_actualizado = actualizar_estado_servicio(servicio_id, body['estado'])
    except Exception as error:
        return jsonify(construir_error_api(
            code="internal.server.error",
            message="Error al actualizar el estado del servicio",
            description=str(error)
        )), 500
    
    return jsonify(servicio_actualizado), 200