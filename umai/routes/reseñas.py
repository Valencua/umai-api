from flask import Blueprint, jsonify, request

from umai.constants import ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_INVALID_BODY
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
			code=ERROR_CODE_INVALID_BODY,
			message='Faltan campos requeridos',
			description='email y fecha son obligatorios'
		)), 400

	try:
		puede_reseñar = validar_usuario_para_reseña(email, fecha)
	except ValueError as exc:
		payload = exc.args[0] if exc.args else construir_error_api(
			code=ERROR_CODE_INVALID_BODY,
			message='Datos inválidos',
			description='No se pudieron validar los parámetros enviados'
		)
		return jsonify(payload), 400
	except Exception:
		return jsonify(construir_error_api(
			code=ERROR_CODE_INTERNAL_SERVER,
			message='Error al validar la reserva',
			description='Ocurrió un error inesperado durante la validación'
		)), 500

	return jsonify({
		'puede_realizar_reseña': puede_reseñar,
		'message': 'Validación completada',
	}), 200
