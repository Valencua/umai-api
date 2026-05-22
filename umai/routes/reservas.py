from flask import Blueprint, jsonify, request
from umai.utils import construir_error_api,validar_entero,validar_minimo
from umai.constants import ERROR_CODE_INVALID_BODY, ERROR_CODES_CONFLICTO, ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_RESERVA_NO_ENCONTRADA
from umai.services.reservas import crear_reserva, obtener_reservas, cancelar_reserva_por_codigo, confirmar_reserva_por_codigo
from umai.validators.reservas import validar_crear_reserva, validar_uuid_codigo,validar_funcion_reserva

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/', methods=['POST'])
def post_reserva():

    body = request.get_json(silent=True)

    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe contener un JSON con los campos: nombre, email, telefono, fecha y cantidad de personas'
        )), 400

    try:
        data = validar_crear_reserva(body)
        crear_reserva(data)

        return '', 201
    except ValueError as e:
        error = e.args[0]
        if error['errors'][0]['code'] in ERROR_CODES_CONFLICTO:
            return jsonify(error), 409
        return jsonify(error), 400
    except Exception as e:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500


@reservas_bp.route('/<uuid_codigo>', methods=['PATCH'])
def patch_reserva(uuid_codigo):
    funcion = request.args.get('funcion')
    try:
        funcion = validar_funcion_reserva(funcion)
        codigo = validar_uuid_codigo(uuid_codigo)
        if funcion == 'confirmar':
            reserva = confirmar_reserva_por_codigo(codigo)
        else:
            reserva = cancelar_reserva_por_codigo(codigo)
        return jsonify(reserva), 200
    except ValueError as e:
        error = e.args[0]
        codigo_error = error['errors'][0]['code']
        if codigo_error == ERROR_CODE_RESERVA_NO_ENCONTRADA:
            return jsonify(error), 404
        if codigo_error in ERROR_CODES_CONFLICTO:
            return jsonify(error), 409
        return jsonify(error), 400
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al procesar la solicitud',
            description='Hubo un error interno'
        )), 500
    
@reservas_bp.route('/', methods=['GET'])
def get_reservas():
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    orden = request.args.get('orden', 'desc').strip().lower()
    uuid_codigo = request.args.get('uuid_codigo')

    errores = []

    if limit is not None:
        try:
            limit = validar_entero(limit, 'limit')
            validar_minimo(limit, 1, 'limit')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if offset is not None:
        try:
            offset = validar_entero(offset, 'offset')
            validar_minimo(offset, 0, 'offset')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if orden not in ('asc', 'desc'):
        errores.append(construir_error_api(
            code='invalid.orden',
            message='orden invalido',
            description="Los valores permitidos son: 'asc', 'desc'"
        )['errors'][0])

    if uuid_codigo is not None:
        try:
            uuid_codigo = validar_uuid_codigo(uuid_codigo)
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        return jsonify({'errors': errores}), 400

    try:
        reservas = obtener_reservas(limit=limit, offset=offset, orden=orden, uuid_codigo=uuid_codigo)
        if uuid_codigo and not reservas:
            return jsonify(construir_error_api(
                code=ERROR_CODE_RESERVA_NO_ENCONTRADA,
                message='Reserva no encontrada',
                description=f'No existe una reserva con el código {uuid_codigo}'
            )), 404

        return jsonify({'data': reservas, 'status': 'success'}), 200
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error listando las reservas',
            description='Ocurrió un error inesperado'
        )), 500