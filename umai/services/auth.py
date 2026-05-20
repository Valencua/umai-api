from db import supabase
from umai.constants import ERROR_CODE_UNAUTHORIZED
from umai.utils import construir_error_api

def autenticar_usuario(usuario: str, contrasena: str) -> dict:

    respuesta = supabase.table('usuarios').select(
        'usuario, contraseña, admin'
    ).eq('usuario', usuario).limit(1).execute()

    if not respuesta.data:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_UNAUTHORIZED,
            message='Credenciales invalidas',
            description='El usuario o la contraseña son incorrectos',
        ), 401)
    
    fila = respuesta.data[0]

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