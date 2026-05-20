from flask import Blueprint, jsonify, request
from umai.services.platos import eliminar_plato, traer_todos_los_platos, crear_plato
from umai.utils import construir_error_api, validar_entero
from umai.validators.platos import validar_crear_plato

from umai.constants import (
    ERROR_CODES_CONFLICTO,
    ERROR_CODE_INTERNAL_SERVER
)


platos_bp = Blueprint('platos', __name__)


@platos_bp.route('/', methods=['POST'])
def post_plato():

    body = request.form.to_dict()

    body['foto'] = request.files.get('foto')

    try:

        data = validar_crear_plato(body)

        plato = crear_plato(data)

        return jsonify(plato), 201

    except ValueError as e:

        error = e.args[0]

        if isinstance(error, dict) and error.get('errors'):

            if error['errors'][0]['code'] in ERROR_CODES_CONFLICTO:

                return jsonify(error), 409

            return jsonify(error), 400

        return jsonify({'errors': error}), 400

    except Exception as e:

        return jsonify(construir_error_api(
        code=ERROR_CODE_INTERNAL_SERVER,
        message='error al procesar la solicitud',
        description=str(e)
    )), 500

@platos_bp.route('/', methods=['GET'])
def listar_platos():
    try:
        platos = traer_todos_los_platos()
        return jsonify({
            'data': platos,
            'status': 'success'
        }), 200

    except Exception:
        return jsonify(construir_error_api(
            'LIST_ERROR',
            'Error listando platos',
            'Error inesperado')
        ), 500

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
            description='Ocurrio un error inesperado'
        )), 500

    return '', 204