from flask import Blueprint, jsonify, request
from umai.constants import ERROR_CODE_INVALID_BODY, ERROR_CODE_INTERNAL_SERVER
from umai.services.reseñas import crear_reseña
from umai.utils import construir_error_api
from umai.validators.reseñas import validar_crear_reseña

reseñas_bp = Blueprint('reseñas', __name__)

@reseñas_bp.route('/', methods=['POST'])
def post_reseña():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con COntent-Type application/json'
        )), 400

    try:
        data = validar_crear_reseña(body)
        reseña = crear_reseña(data)
        return jsonify({'data': reseña, 'status': 'success'}), 201

    except ValueError as e:
        return jsonify(e.args[0]),400
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='No se puede crear la reseña',
            description='Ocurrio un error inesperado'
        )), 500