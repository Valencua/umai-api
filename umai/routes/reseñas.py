from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api, validar_entero
from umai.services.reseñas import listar_reseñas, eliminar_reseña, crear_reseña, actualizar_estado_reseña
from umai.validators.reseñas import  validar_crear_reseña
from umai.constants import ERROR_CODE_NOT_FOUND, ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_INVALID_BODY

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

@reseñas_bp.route('/<string:resena_id>', methods=['DELETE'])
def delete_reseña(resena_id):
    try:
        id_validado = validar_entero(resena_id, 'resena_id')
        eliminar_reseña(id_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al eliminar la reseña',
            description='Ocurrió un error inesperado'
        )), 500

    return '', 204

@reseñas_bp.route('/', methods=['POST'])
def post_reseña():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400
    try:
        data = validar_crear_reseña(body)
        reseña = crear_reseña(data)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al crear la reseña',
            description='Ocurrió un error inesperado'
        )), 500
    return jsonify(reseña), 201

@reseñas_bp.route('/<string:resena_id>', methods=['PATCH'])
def patch_estado_reseña(resena_id):
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        id_validado = validar_entero(resena_id, 'resena_id')
        reseña_actualizada = actualizar_estado_reseña(id_validado, body['estado'])
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al actualizar el estado de la reseña',
            description='Ocurrió un error inesperado'
        )), 500

    return jsonify(reseña_actualizada), 200