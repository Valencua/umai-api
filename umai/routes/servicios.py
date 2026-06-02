from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api, validar_entero
from umai.services.servicios import obtener_servicios, crear_servicio, actualizar_estado_servicio
from umai.validators.servicios import validar_crear_servicio, validar_actualizar_estado_servicio

from umai.constants import (
    ERROR_CODE_INVALID_BODY, 
    ERROR_CODE_INTERNAL_SERVER,
    ERROR_CODES_CONFLICTO
    )


servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/', methods=['GET'])
def traer_servicios():
    try:
        servicios = obtener_servicios()

    except ValueError as e:
        return jsonify(e.args[0]), 404        
    except Exception as error:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message="Error al obtener los servicios",
            description=str(error)
        )), 500
    
    return jsonify(servicios), 200

@servicios_bp.route('/', methods=['POST'])
def post_servicio():
    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        data = validar_crear_servicio(body)
        servicio = crear_servicio(data)
    except ValueError as e:
        error = e.args[0]
        if isinstance(error, dict) and error.get('errors'):
            if error['errors'][0]['code'] in ERROR_CODES_CONFLICTO:
                return jsonify(error), 409
        return jsonify(error), 400
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500
    
    return jsonify(servicio), 201

@servicios_bp.route('/<id>', methods=['PATCH'])
def patch_estado_servicio(id):

    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        )), 400

    try:
        id_validado = validar_entero(id, 'id')
        estado_validado = validar_actualizar_estado_servicio(body)
        actualizar_estado_servicio(id_validado, estado_validado)
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception as error:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message="Error al actualizar el estado del servicio",
            description='Hubo un error interno'
        )), 500
    
    return '', 204

