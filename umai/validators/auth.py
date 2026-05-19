from umai.constants import (
    CONTRASENA_MAX,
    CONTRASENA_MIN,
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_MISSING_FIELDS,
    USUARIO_MAX,
    USUARIO_MIN,
)
from umai.utils import construir_error_api, validar_longitud

def validar_login(body) -> dict:
    if not isinstance(body, dict):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON con "usuario" y "contraseña"'
        ))

    errores = []
    faltantes = []
    for campo in ('usuario', 'contraseña'):
        if not body.get(campo):
            faltantes.append(campo)
    
    if faltantes:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_MISSING_FIELDS,
            message='Faltan campos requeridos',
            description=f'Los siguientes campos son obligatorios: {", ".join(faltantes)}',
        )['errors'][0])
        raise ValueError({'errors': errores})
    
    usuario = str(body['usuario']).strip()
    contrasena = str((body['contraseña']))

    try:
        validar_longitud(usuario, 'usuario', min=USUARIO_MIN, max=USUARIO_MAX)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_longitud(contrasena, 'contraseña', min=CONTRASENA_MIN, max=CONTRASENA_MAX)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    
    if errores:
        raise ValueError({'errors': errores})
    
    return {
        'usuario': usuario,
        'contraseña': contrasena,
    }