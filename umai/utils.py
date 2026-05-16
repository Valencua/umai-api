"""
Para manejar las excepciones, errores, etc. (Más que nada lo vamos a utilizar
para utilizarlo como handler global)
"""



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

def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(f"Valor por debajo del mínimo: '{nombre}' es {valor}, mínimo esperado {minimo}")

        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por debajo del mínimo permitido',
            description=f"El parámetro '{nombre}' debe ser mayor o igual a {minimo}. Se recibió: {valor}"
        ))

    return valor