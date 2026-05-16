from umai.utils import construir_error_api, validar_longitud

def validar_crear_servicio(body: dict) -> dict:
    errores = []
    campos_requeridos = ['nombre', 'descripcion', 'icono']
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
        validar_longitud(body['nombre'], 'nombre', min=5, max=100)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_longitud(body['descripcion'], 'descripcion', min=10, max=500)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        validar_longitud(body['icono'], 'icono', min=1, max=10)
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre':      body['nombre'].strip(),
        'descripcion': body['descripcion'].strip(),
        'icono':       body['icono'].strip(),
        'estado':      body.get('estado', True)
    }