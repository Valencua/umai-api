from db.connection import fetch_one
from umai.constants import ERROR_CODE_UNAUTHORIZED
from umai.utils import construir_error_api


def autenticar_usuario(usuario: str, contrasena: str) -> dict:

    fila = fetch_one(
        """
        SELECT usuario, contraseña, admin
        FROM usuarios
        WHERE usuario = %s
        LIMIT 1
        """,
        (usuario,),
    )

    if not fila:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_UNAUTHORIZED,
            message='Credenciales invalidas',
            description='El usuario o la contraseña son incorrectos',
        ), 401)

    if fila['contraseña'] != contrasena:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_UNAUTHORIZED,
            message='Credenciales invalidas',
            description='El usuario o la contraseña son incorrectos',
        ), 401)

    return {
        'usuario': fila['usuario'],
        'admin': bool(fila['admin']),
    }