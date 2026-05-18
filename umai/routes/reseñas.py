from flask import Blueprint, jsonify, request
from umai.constants import ERROR_CODE_INVALID_BODY, ERROR_CODE_INTERNAL_SERVER
from umai.services.reseñas import listar_reseñas
from umai.utils import construir_error_api

reseñas_bp = Blueprint('reseñas', __name__)

@reseñas_bp.route('/', methods=['GET'])
def get_reseñas():
    estado = request.args.get('estado')

    if estado is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Falta el parametro estado',
            description='Debe indicar estado=true o estado=false al final de la URL'
        )), 400
    elif estado.lower() == 'true':
        estado_bool = True
    elif estado.lower() == 'false':
        estado_bool = False
    else:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Parametro de estado invalido',
            description='El parametro estado solo acepta true o false'
        )), 400


    try:
        reseñas = listar_reseñas(estado_bool)
        return jsonify({'data': reseñas, 'status': 'success'}), 200
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='No se pudieron obtener las reseñas',
            description='Ocurrio un error inesperado'
        )), 500
