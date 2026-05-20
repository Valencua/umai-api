from db import supabase
from umai.utils import construir_error_api, validar_longitud, validar_minimo, validar_maximo, validar_entero
from umai.constants import ESTADO_RESERVA_CONFIRMADO

def validar_id_reseña(id_reseña: str) -> int:
    return validar_entero(id_reseña, 'id')

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

def validar_existe_cliente(email: str) -> dict:
    respuesta = (
        supabase.table('clientes')
        .select('cliente_id')
        .eq('email', email)
        .limit(1)
        .execute()
    )
    return respuesta.data[0] if respuesta.data else None

def cliente_tiene_reservas_confirmadas(cliente_id: int):
    respuesta = (
        supabase.table('reservas')
        .select('reserva_id')
        .eq('cliente_id', cliente_id)
        .eq('estado', ESTADO_RESERVA_CONFIRMADO)
        .execute()
    )
    return respuesta

def cliente_tiene_reseña(cliente_id: int):
    respuesta = (
        supabase.table('reseñas')
        .select('reseña_id')
        .eq('cliente_id', cliente_id)
        .limit(1)
        .execute()
    )
    return respuesta