import logging
import uuid as uuid_lib
from datetime import datetime, timezone
from umai.constants import (
    FORMATO_FECHA_STR_zoneinfo,
    HORA_APERTURA,
    HORA_CIERRE,
    MAX_PERSONAS,
    MIN_PERSONAS,
    MINUTO_APERTURA,
    MINUTO_CIERRE,
    TELEFONO_MAX_LONGITUD,
    TELEFONO_MIN_LONGITUD,
    ERROR_CODE_UUID_CODIGO_INVALIDO,
    ERROR_CODE_INVALID_FECHA,
    ERROR_CODE_INVALID_HORARIO,
    FUNCIONES_VALIDAS,
    ERROR_CODE_MISSING_FECHA,
    ERROR_CODE_INVALID_FORMAT_FECHA,
    FORMATO_FECHA,
    ERROR_CODE_INVALID_BODY

)
from umai.utils import (
    a_utc,
    construir_error_api,
    fecha_hora_futura,
    horario_en_rango_servicio,
    validar_email,
    validar_entero,
    validar_formato_fecha,
    validar_longitud,
    validar_maximo,
    validar_minimo,
    validar_telefono,
    validar_solo_letras,
    TZ_LOCAL,
)

logger = logging.getLogger(__name__)

def validar_uuid_codigo(uuid_codigo: str) -> str:
    if not uuid_codigo or not str(uuid_codigo).strip():
        raise ValueError(construir_error_api(
            code='required.uuid_codigo',
            message="Campo requerido: 'uuid_codigo'",
            description='El código de la reserva es obligatorio'
        ))

    try:
        return str(uuid_lib.UUID(str(uuid_codigo).strip()))
    except ValueError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_UUID_CODIGO_INVALIDO,
            message="Formato de 'uuid_codigo' inválido",
            description='El código debe ser un UUID válido (ej. a3f2b1c4-5678-90ab-cdef-1234567890ab)'
        ))


def validar_crear_reserva(body: dict) -> dict:
    errores = []
    campos_requeridos = ['nombre', 'email', 'telefono', 'fecha', 'cantidad_personas']

    for campo in campos_requeridos:
        if campo not in body or body[campo] in (None, ''):
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    nombre = body['nombre'].strip()
    email = body['email'].strip().lower()
    telefono = body['telefono'].strip()
    fecha = body['fecha'].strip()
    logger.debug(f"Fecha ingresada: {fecha}")
    try:
        validar_longitud(nombre, 'nombre', min=3, max=100)
        validar_solo_letras(nombre, 'nombre')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_longitud(email, 'email', min=5, max=100)
        validar_email(email)
    except ValueError as e:
        if isinstance(e.args[0], dict):
            errores.extend(e.args[0]['errors'])

    try:
        validar_longitud(telefono, 'telefono', min=TELEFONO_MIN_LONGITUD, max=TELEFONO_MAX_LONGITUD)
        telefono = validar_telefono(telefono)
    except ValueError as e:
        if isinstance(e.args[0], dict):
            errores.extend(e.args[0]['errors'])

    cantidad_personas = body['cantidad_personas']
    try:
        if not isinstance(cantidad_personas, int):
            cantidad_personas = validar_entero(str(cantidad_personas), 'cantidad_personas')
        validar_minimo(cantidad_personas, MIN_PERSONAS, 'cantidad_personas')
        validar_maximo(cantidad_personas, MAX_PERSONAS, 'cantidad_personas')
    except ValueError as e:
        if isinstance(e.args[0], dict):
            errores.extend(e.args[0]['errors'])

    fecha_hora_local = None
    
    try:
        obj_fecha = validar_formato_fecha(fecha,'%Y-%m-%dT%H:%M:%S.%f%z', 'fecha')

        if not horario_en_rango_servicio(obj_fecha.hour, obj_fecha.minute):
            raise ValueError(construir_error_api(
                code=ERROR_CODE_INVALID_HORARIO,
                message="Horario fuera del rango de atención",
                description=(
                    f'El horario debe estar entre las {HORA_APERTURA:02d}:{MINUTO_APERTURA:02d} '
                    f'y las {HORA_CIERRE:02d}:{MINUTO_CIERRE:02d} hs'
                )
            ))

        fecha_hora_local = obj_fecha.astimezone(TZ_LOCAL) #Nada más quiero asegurar que el ZoneTime figure como GMT-3

        if not fecha_hora_futura(fecha_hora_local):
            raise ValueError(construir_error_api(
                code=ERROR_CODE_INVALID_FECHA,
                message='Fecha y horario en el pasado',
                description='La reserva debe ser para una fecha y horario futuros'
            ))
    except ValueError as e:
        if isinstance(e.args[0], dict):
            if 'errors' in e.args[0]:
                errores.extend(e.args[0]['errors'])
            else:
                errores.append(e.args[0])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre': nombre,
        'email': email,
        'telefono': telefono,
        'fecha': fecha,
        'fecha_hora_local': fecha_hora_local,
        'fecha_hora_utc': a_utc(fecha_hora_local),
        'cantidad_personas': cantidad_personas,
    }

def validar_fecha_disponibilidad(fecha: str):
    if not fecha or not fecha.strip():
        raise ValueError(construir_error_api(
            code=ERROR_CODE_MISSING_FECHA,
            message='Fecha requerida',
            description='Debe enviar la fecha en formato YYYY-MM-DD'
        ))
    try:
        fecha_obj = datetime.strptime(fecha.strip(), FORMATO_FECHA).date()
    except ValueError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_FORMAT_FECHA,
            message='Fecha inválida',
            description='La fecha debe tener formato YYYY-MM-DD'
        ))
    hoy = datetime.now(TZ_LOCAL).date()

    if fecha_obj < hoy:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_FECHA,
            message='Fecha inválida',
            description='No se puede consultar disponibilidad para fechas pasadas'
        ))

    return fecha_obj

def validar_patch_reserva(uuid_codigo: str, body: dict | None) -> dict:
    if body is None or not isinstance(body, dict):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud invalido',
            description="El body debe ser un JSON con el campo 'funcion'"
        ))

    funcion = body.get('funcion')
    if not funcion or not str(funcion).strip():
        raise ValueError(construir_error_api(
            code='required.funcion',
            message='funcion es requerida',
            description="El campo 'funcion' es obligatorio en el body"
        ))

    funcion = str(funcion).strip().lower()
    if funcion not in FUNCIONES_VALIDAS:
        raise ValueError(construir_error_api(
            code='invalid.funcion',
            message='funcion invalida',
            description="Los valores permitidos son: 'cancelar', 'confirmar'"
        ))

    return {
        'uuid_codigo': validar_uuid_codigo(uuid_codigo),
        'funcion': funcion,
    }

def validar_cantidad_personas_disponibilidad(cantidad_personas: str | None) -> int | None:
    if cantidad_personas is None:
        return None

    try:
        cantidad = validar_entero(cantidad_personas, 'cantidad_personas')
        validar_minimo(cantidad, MIN_PERSONAS, 'cantidad_personas')
        validar_maximo(cantidad, MAX_PERSONAS, 'cantidad_personas')
    except ValueError as e:
        raise ValueError(e.args[0])

    return cantidad