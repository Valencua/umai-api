from flask import Blueprint, jsonify, request
from umai.constants import ERROR_CODE_INTERNAL_SERVER, ERROR_CODE_INVALID_BODY
from umai.services.auth import autenticar_usuario
from umai.utils import construir_error_api
from umai.validators.auth import validar_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def post_login():
    body = request.get_json(silent=True)
    
    if body is None:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con Content-Type application/json'
        )),400

    try:
        datos = validar_login(body)
        usuario = autenticar_usuario(datos['usuario'], datos['contraseña'])
    except ValueError as e:
        status = e.args[1] if len(e.args) > 1 else 400
        return jsonify(e.args[0]), status
    except Exception:
        return jsonify(construir_error_api(
            code=ERROR_CODE_INTERNAL_SERVER,
            message='Error al procesar la solicitud',
            description='Hubo un error interno',
        )), 500

    return jsonify({'admin': usuario['admin']}), 200