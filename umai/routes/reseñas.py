from flask import Blueprint, jsonify 
from umai.constants import ERROR_CODE_NOT_FOUND, ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_INVALID_BODY
from umai.utils import construir_error_api
from umai.validators.reseñas import validar_id_reseña
from umai.services.reseñas import eliminar_reseña

reseñas_bp = Blueprint('reseñas', __name__)

@reseñas_bp.route('/<id>', methods=['DELETE'])
def delete_reseña(id):
    try:
        reseña_id_entero = validar_id_reseña(id)
    except ValueError as exc:
        payload = exc.args[0] if exc.args else construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Formato de ID inválido',
            description='El ID proporcionado debe ser un número entero'
        )
        return jsonify(payload), 400
    
    resultado = eliminar_reseña(reseña_id_entero)

    if resultado is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error interno del servidor',
            description='Ocurrió un error al intentar eliminar la reseña'
        )), 500
    
    if not resultado:
        return jsonify(construir_error_api(
            code=ERROR_CODE_NOT_FOUND,
            message='Reseña no encontrada',
            description=f'No se encontró una reseña con ID {reseña_id_entero}'
        )), 404
    
    return jsonify({'message': f'Reseña con ID {reseña_id_entero} eliminada exitosamente'}), 200