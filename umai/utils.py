"""
Para manejar las excepciones, errores, etc. (Más que nada lo vamos a utilizar
para utilizarlo como handler global)
""""""
Para manejar las excepciones, errores, etc. (Más que nada lo vamos a utilizar
para utilizarlo como handler global)
"""

import logging
import re
from datetime import datetime, timezone
from re import sub
from zoneinfo import ZoneInfo

from umai.constants import (
    ERROR_CODE_INVALID_MAX_VALUE,
    ERROR_CODE_INVALID_MIN_VALUE,
    FORMATO_FECHA,
    FORMATO_HORARIO,
    HORA_APERTURA,
    HORA_CIERRE,
    MINUTO_APERTURA,
    MINUTO_CIERRE,
    TELEFONO_MAX_DIGITOS,
    TELEFONO_MIN_DIGITOS,
    TZ_LOCAL_NAME,
)

logger = logging.getLogger(__name__)

TZ_LOCAL = ZoneInfo(TZ_LOCAL_NAME)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
TELEFONO_RE = re.compile(r'^\+?[\d\s\-().]+$')


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }


def validar_longitud(valor: str, campo: str, min: int = None, max: int = None) -> None:
    errores = []

    if min is not None and len(valor) < min:
        errores.append(construir_error_api(
            code=f'invalid.{campo}.length',
            message=f"'{campo}' demasiado corto",
            description=f"El campo '{campo}' debe tener al menos {min} caracteres"
        )['errors'][0])

    if max is not None and len(valor) > max:
        errores.append(construir_error_api(
            code=f'invalid.{campo}.length',
            message=f"'{campo}' demasiado largo",
            description=f"El campo '{campo}' no puede superar los {max} caracteres"
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})


def validar_formato_fecha(fecha: str, formato: str, nombre: str = 'fecha') -> datetime:
    try:
        return datetime.strptime(fecha, formato)
    except ValueError:
        logger.warning(f"Formato de fecha inválido: '{fecha}' no cumple el formato '{formato}'")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{fecha}' no cumple el formato esperado '{formato}'"
        ))


def validar_entero(numero: str, nombre: str = 'numero') -> int:
    numero_sin_letras = sub('[a-zA-Z]+', '', numero)

    try:
        return int(numero_sin_letras)
    except ValueError:
        logger.warning(f"Valor numérico inválido: '{numero}' no puede convertirse a entero")

        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}.format',
            message=f"Formato de '{nombre}' inválido",
            description=f"El valor '{numero}' no puede convertirse a un número entero"
        ))


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(f"Valor por debajo del mínimo: '{nombre}' es {valor}, mínimo esperado {minimo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por debajo del mínimo permitido',
            description=f"El parámetro '{nombre}' debe ser mayor o igual a {minimo}. Se recibió: {valor}"
        ))

    return valor


def validar_maximo(valor: int, maximo: int, nombre: str) -> int:
    if valor > maximo:
        logger.warning(f"Valor por encima del máximo: '{nombre}' es {valor}, máximo esperado {maximo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message='Valor por encima del máximo permitido',
            description=f"El parámetro '{nombre}' debe ser menor o igual a {maximo}. Se recibió: {valor}"
        ))

    return valor


def validar_email(email: str) -> str:
    if not EMAIL_RE.match(email):
        logger.warning(f"Email inválido: '{email}'")

        raise ValueError(construir_error_api(
            code='invalid.email.format',
            message="Formato de 'email' inválido",
            description=f"El valor '{email}' no es un email válido"
        ))

    return email


def validar_telefono(telefono: str) -> str:
    telefono = telefono.strip()

    if not TELEFONO_RE.match(telefono):
        logger.warning(f"Teléfono inválido: '{telefono}'")

        raise ValueError(construir_error_api(
            code='invalid.telefono.format',
            message="Formato de 'telefono' inválido",
            description=(
                'El teléfono solo puede contener dígitos, espacios, guiones, paréntesis '
                'y un "+" opcional al inicio'
            )
        ))

    digitos = sub(r'\D', '', telefono)
    if not (TELEFONO_MIN_DIGITOS <= len(digitos) <= TELEFONO_MAX_DIGITOS):
        logger.warning(f"Teléfono con cantidad de dígitos inválida: '{telefono}'")

        raise ValueError(construir_error_api(
            code='invalid.telefono.format',
            message="Formato de 'telefono' inválido",
            description=(
                f'El teléfono debe tener entre {TELEFONO_MIN_DIGITOS} y {TELEFONO_MAX_DIGITOS} '
                'dígitos (incluido código de país). '
                "Ejemplos: '+54 9 11 1234 5678', '+1 555 123 4567'"
            )
        ))

    return telefono

def combinar_fecha_horario(fecha: str, horario: str) -> datetime:
    dt_naive = datetime.strptime(f'{fecha} {horario}', f'{FORMATO_FECHA} {FORMATO_HORARIO}')
    return dt_naive.replace(tzinfo=TZ_LOCAL)

def a_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_LOCAL)
    return dt.astimezone(timezone.utc)

def a_local(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_LOCAL)

def formatear_rfc3339(dt: datetime) -> str:
    local = a_local(dt) if dt.tzinfo else dt.replace(tzinfo=TZ_LOCAL)
    return local.isoformat(timespec='microseconds')

def horario_en_rango_servicio(hora: int, minuto: int) -> bool:
    minutos = hora * 60 + minuto
    apertura = HORA_APERTURA * 60 + MINUTO_APERTURA
    cierre = HORA_CIERRE * 60 + MINUTO_CIERRE
    return minutos >= apertura or minutos <= cierre

def fecha_hora_futura(dt_local: datetime) -> bool:
    return dt_local >= datetime.now(TZ_LOCAL)

def validar_solo_letras(valor: str, campo: str) -> None:
    if not re.match(r'^[a-zA-Z\s]+$', valor):
        raise ValueError({'errors': [construir_error_api(
            code=f'invalid.{campo}.format',
            message=f"'{campo}' contiene caracteres inválidos",
            description=f"El campo '{campo}' solo puede contener letras y espacios"
        )['errors'][0]]})