from umai.utils import construir_error_api, validar_longitud, validar_minimo
import logging

from umai.constants import ERROR_CODE_INVALID_MIN_VALUE

logger = logging.getLogger(__name__)

def validar_maximo(valor: int, maximo: int, nombre: str) -> int:
    if valor > maximo:
        logger.warning(f"Valor por encima del maximo: '{nombre}' es {valor}, maximo esperado {maximo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por encima del maximo permitido',
            description=f"El parámetro '{nombre}' debe ser menor o igual a {maximo}. Se recibió: {valor}"
        ))

    return valor

def validar_crear_reserva(body: dict) -> dict:
    errores = []
    campos_requeridos = ['nombre', 'email', 'telefono', 'fecha', 'horario', 'cantidad_personas']
    for campo in campos_requeridos:
        if campo not in body or not body[campo]:
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])
    if errores:
        raise ValueError({'errors': errores})
    try:
        validar_longitud(body['nombre'], 'nombre', min=3, max=100)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    try:
        validar_longitud(body['email'], 'email', min=11, max=100) #Falta validar que siga formato email
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    try:
        validar_longitud(body['telefono'], 'telefono', min=9, max=13)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    try:
        validar_minimo(body['cantidad_personas'], 1, 'cantidad_personas') #Chequear que campos sean int 
        validar_maximo(body['cantidad_personas'], 5, 'cantidad_personas')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    #Falta formato fecha

    if errores:
        raise ValueError({'errors': errores})
    return {
        'nombre': body['nombre'].strip(),
        'email': body['email'].strip(),
        'telefono': body['telefono'].strip(),
        'fecha': body['fecha'].strip(),
        'horario': body['horario'].strip(),
        'cantidad_personas': body['cantidad_personas']
    }