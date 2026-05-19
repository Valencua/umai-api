from flask import Blueprint, jsonify, request

from umai.validators.platos import validar_crear_plato
from umai.services.platos import crear_plato

platos_bp = Blueprint('platos', __name__)

@platos_bp.route('/', methods=['POST'])
def post_plato():

    body = request.form.to_dict()

    foto = request.files.get('foto')

    body['foto'] = foto

    try:

        data = validar_crear_plato(body)

        plato = crear_plato(data)

    except ValueError as e:

        return jsonify({
            'errors': e.args[0]
        }), 400

    except Exception as e:

        print(e)

        return jsonify({
            'error': 'Hubo un error interno'
        }), 500

    return jsonify(plato), 201