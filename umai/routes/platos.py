from flask import Blueprint, jsonify
from umai.services.platos import eliminar_plato
from umai.utils import construir_error_api, validar_entero
from umai.constants import ERROR_CODE_INTERNAL_SERVER

platos_bp = Blueprint('platos', __name__)

@platos_bp.route('/<string:plato_id>', methods=['DELETE'])
def delete_plato(plato_id):
    try:
        id_validado = validar_entero(plato_id, 'plato_id')
        eliminar_plato(id_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al eliminar el plato',
            description='OcurriÃ³ un error inesperado'
        )), 500

    return '', 204