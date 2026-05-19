from flask import Blueprint, jsonify, request

from umai.validators.platos import validar_crear_plato
from umai.services.platos import crear_plato, traer_todos_los_platos
from umai.utils import construir_error_api

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



