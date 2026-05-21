from umai.utils import construir_error_api, validar_longitud, validar_minimo, validar_maximo, validar_email

def validar_crear_reseña(body: dict) -> dict:
    errores = []
    campos_requeridos = ['email', 'rating', 'descripcion']

    for campo in campos_requeridos:
        if campo not in body or body[campo] is None:
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    try:
        validar_email(body['email'])
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_longitud(str(body['descripcion']), 'descripcion', min=10, max=500)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    rating = body['rating']
    if not isinstance(rating, int):
        errores.append(construir_error_api(
            code='invalid.rating.format',
            message="Formato de 'rating' inválido",
            description='El rating debe ser un número entero'
        )['errors'][0])
    else:
        try:
            validar_minimo(rating, 1, 'rating')
            validar_maximo(rating, 5, 'rating')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'email':       body['email'].strip(),
        'descripcion': body['descripcion'].strip(),
        'rating':      rating
    }
