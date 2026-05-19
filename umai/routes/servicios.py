from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api
from umai.services.servicios import obtener_servicios, crear_servicio, actualizar_estado_servicio
from umai.validators.servicios import validar_crear_servicio

from umai.constants import (
    ERROR_CODE_INVALID_BODY, 
    ERROR_CODE_INTERNAL_SERVER
    )


servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/', methods=['GET'])
def traer_servicios():
    try:
        servicios = obtener_servicios()

        if not servicios:
            return jsonify(construir_error_api(
                code='not_found.servicios.empty',
                message="No se encontraron servicios",
                description="No existen servicios registrados en la base de datos actualmente."
            )), 404
            
    except Exception as error:
        return jsonify(construir_error_api(
            code="internal.server.error",
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
        return jsonify(e.args[0]), 400
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
        servicio_actualizado = actualizar_estado_servicio(id, body['estado'])
    except Exception as error:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message="Error al actualizar el estado del servicio",
            description='Hubo un error interno'
        )), 500
    
    return jsonify(servicio_actualizado), 200

