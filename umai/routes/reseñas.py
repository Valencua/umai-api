from flask import Blueprint, jsonify, request

from umai.services.reseñas import listar_reseñas, validar_usuario_para_reseña, eliminar_reseña, crear_reseña
from umai.utils import construir_error_api
from umai.validators.reseñas import validar_id_reseña, validar_crear_reseña

from umai.constants import ERROR_CODE_NOT_FOUND, ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_INVALID_BODY

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

@reseñas_bp.route('/<id>', methods=['DELETE'])
def delete_reseña(id):
    try:
        reseña_id_entero = validar_id_reseña(id)
    except ValueError as exc:
        payload = exc.args[0] if exc.args else construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Formato de ID inválido',
            description='El ID proporcionado debe ser un número entero'
        )
        return jsonify(payload), 400
    
    resultado = eliminar_reseña(reseña_id_entero)

    if resultado is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error interno del servidor',
            description='Ocurrió un error al intentar eliminar la reseña'
        )), 500
    
    if not resultado:
        return jsonify(construir_error_api(
            code=ERROR_CODE_NOT_FOUND,
            message='Reseña no encontrada',
            description=f'No se encontró una reseña con ID {reseña_id_entero}'
        )), 404
    
    return jsonify({'message': f'Reseña con ID {reseña_id_entero} eliminada exitosamente'}), 200

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

