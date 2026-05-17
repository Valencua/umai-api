
from flask import Blueprint, jsonify, request

import logging
from umai.utils import construir_error_api
from umai.services.platos import traer_todos_los_platos

platos_bp = Blueprint('platos', __name__)

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


