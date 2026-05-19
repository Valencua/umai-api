from flask import Blueprint, jsonify, request

from umai.constants import (
    ERROR_CODES_CONFLICTO,
    ERROR_CODE_INTERNAL_SERVER
)

from umai.services.platos import crear_plato
from umai.utils import construir_error_api
from umai.validators.platos import validar_crear_plato

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

        print(e)
        
        return jsonify(construir_error_api(
        code=ERROR_CODE_INTERNAL_SERVER,
        message='error al procesar la solicitud',
        description=str(e)
    )), 500

