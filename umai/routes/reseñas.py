from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api
from umai.services.reseñas import actualizar_estado_reseña
from ..constants import ERROR_CODE_INVALID_BODY
from ..constants import ERROR_CODE_INTERNAL_SERVER

reseñas_bp = Blueprint('reseñas', __name__)


@reseñas_bp.route('/<id>', methods=['PATCH'])
def patch_estado_reseña(id):
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        reseña_actualizada = actualizar_estado_reseña(id, body['estado'])
    except Exception as error:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message="Error al actualizar el estado de la reseña",
            description=str(error)
        )), 500
    
    return jsonify(reseña_actualizada), 200