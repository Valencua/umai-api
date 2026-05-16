import logging
from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api
from umai.services.reservas import obtener_reservas_hoy as obtener_reservas_hoy_service
reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/hoy/', methods=['GET'])
def obtener_reservas_hoy():
    try:
        reservas = obtener_reservas_hoy_service()
        if reservas is not None:
            return jsonify(reservas), 200
        else:
            return jsonify(construir_error_api(
                code='reservas.not_found',
                message='No se encontraron reservas para hoy',
                description='No hay reservas registradas para la fecha actual'
            )), 404
    except Exception as e:
        logging.error(f"Error al obtener reservas: {e}")
        return jsonify(construir_error_api(
            code='reservas.error',
            message='Error al obtener reservas',
            description='Ocurrió un error al intentar obtener las reservas para hoy'
        )), 500



