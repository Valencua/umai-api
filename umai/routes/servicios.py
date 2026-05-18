from flask import Blueprint, jsonify
from umai.utils import construir_error_api
from umai.services.servicios import obtener_servicios

from ..constants import (
    ERROR_CODE_INVALID_BODY)

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
