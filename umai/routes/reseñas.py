from flask import Blueprint, jsonify, request

from umai.services.reseñas import validar_usuario_para_reseña
from umai.utils import construir_error_api

reseñas_bp = Blueprint('reseñas', __name__)


@reseñas_bp.route('/', methods=['GET'])
def puede_realizar_reseña():
	data = request.get_json(silent=True) or {}
	email = data.get('email')
	fecha = data.get('fecha')

	if not email or not fecha:
		return jsonify(construir_error_api(
			code='MISSING_FIELDS',
			message='Faltan campos requeridos',
			description='email y fecha son obligatorios'
		)), 400

	puede_reseñar = validar_usuario_para_reseña(email, fecha)

	if puede_reseñar is None:
		return jsonify(construir_error_api(
			code='VALIDATION_ERROR',
			message='Error al validar la reserva',
			description='Ocurrió un error inesperado durante la validación'
		)), 500

	return jsonify(construir_error_api(
		code='SUCCESS',
		message='Validación completada',
		description='El usuario puede realizar una reseña'
	)), 200
