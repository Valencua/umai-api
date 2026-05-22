from umai.utils import construir_error_api, validar_longitud, validar_minimo, validar_maximo, validar_email, validar_entero

def validar_crear_reseña(body: dict) -> dict:
    errores = []
    campos_requeridos = ['email', 'rating', 'descripcion']
    for campo in campos_requeridos:
        if campo not in body or body[campo] in (None, ''):
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])
    if errores:
        raise ValueError({'errors': errores})
    email = body['email'].strip().lower()
    try:
        validar_email(email)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    try:
        validar_longitud(str(body['descripcion']).strip(), 'descripcion', min=10, max=500)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    rating = body['rating']
    if not isinstance(rating, int):
        try:
            rating = validar_entero(str(rating), 'rating')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])
    if isinstance(rating, int):
        try:
            validar_minimo(rating, 0, 'rating')
            validar_maximo(rating, 5, 'rating')
        except ValueError as e:
            errores.extend(e.args[0]['errors'])
    if errores:
        raise ValueError({'errors': errores})
    return {
        'email': email,
        'descripcion': body['descripcion'].strip(),
        'rating': rating,
    }
