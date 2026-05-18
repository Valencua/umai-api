import logging
from umai.utils import construir_error_api, validar_longitud, validar_minimo, validar_maximo

logger = logging.getLogger(__name__)

def validar_crear_reseña(body: dict) -> dict:
    errores = []
    campos_requeridos = ['cliente_id', 'descripcion', 'rating']

    for campo in campos_requeridos:
        if campo not in body or body[campo] is None:
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacio"    
            )['errors'][0])      

    if errores:
        raise ValueError({'errors': errores})

    descripcion = body['descripcion']
    rating = body['rating']

    try:
        validar_longitud(str(descripcion), 'descripcion', min=3, max=500)
    except ValueError as e:
        if isinstance(e.args[0], dict):
            errores.extend(e.args[0]['errors'])

    if not isinstance(rating, int):
        errores.append(construir_error_api(
            code='invalid.rating.format',
            message='Formato de "rating" invalido',
            description='El rating debe ser un numero entero'
        )['errors'][0])
    else:
        try:
            validar_minimo(rating, 1, 'rating')
            validar_maximo(rating, 5, 'rating')
        except ValueError as e:
            if isinstance(e.args[0], dict) and 'errors' in e.args[0]:
                errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return{
        'cliente_id': body['cliente_id'],
        'descripcion': descripcion,
        'rating': rating
    }                    