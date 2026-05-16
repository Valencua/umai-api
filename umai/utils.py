"""
Para manejar las excepciones, errores, etc. (Más que nada lo vamos a utilizar
para utilizarlo como handler global)
"""

import re

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

def validar_solo_letras(valor: str, campo: str) -> None:
    if not re.match(r'^[a-zA-Z\s]+$', valor):
        raise ValueError({'errors': [construir_error_api(
            code=f'invalid.{campo}.format',
            message=f"'{campo}' contiene caracteres inválidos",
            description=f"El campo '{campo}' solo puede contener letras y espacios"
        )['errors'][0]]})