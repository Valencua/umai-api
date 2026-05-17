import logging

from umai.constants import (
    FORMATO_FECHA,
    FORMATO_HORARIO,
    HORA_APERTURA,
    HORA_CIERRE,
    MAX_PERSONAS,
    MIN_PERSONAS,
    MINUTO_APERTURA,
    MINUTO_CIERRE,
    TELEFONO_MAX_LONGITUD,
    TELEFONO_MIN_LONGITUD,
)
from umai.utils import (
    a_utc,
    combinar_fecha_horario,
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
)

logger = logging.getLogger(__name__)


def validar_crear_reserva(body: dict) -> dict:
    errores = []
    campos_requeridos = ['nombre', 'email', 'telefono', 'fecha', 'horario', 'cantidad_personas']

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
    horario = body['horario'].strip()

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
        validar_formato_fecha(fecha, FORMATO_FECHA, 'fecha')
        horario_dt = validar_formato_fecha(horario, FORMATO_HORARIO, 'horario')

        if not horario_en_rango_servicio(horario_dt.hour, horario_dt.minute):
            raise ValueError(construir_error_api(
                code='invalid.horario.range',
                message="Horario fuera del rango de atención",
                description=(
                    f'El horario debe estar entre las {HORA_APERTURA:02d}:{MINUTO_APERTURA:02d} '
                    f'y las {HORA_CIERRE:02d}:{MINUTO_CIERRE:02d} hs'
                )
            ))

        fecha_hora_local = combinar_fecha_horario(fecha, horario)

        if not fecha_hora_futura(fecha_hora_local):
            raise ValueError(construir_error_api(
                code='invalid.fecha.past',
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
        'horario': horario,
        'fecha_hora_local': fecha_hora_local,
        'fecha_hora_utc': a_utc(fecha_hora_local),
        'cantidad_personas': cantidad_personas,
    }
