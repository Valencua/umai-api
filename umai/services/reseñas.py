from db import supabase
from datetime import datetime
from umai.utils import a_utc, construir_error_api




def listar_reseñas(estado: bool)-> list:
    respuesta = (
        supabase.table('reseñas')
        .select('reseña_id, descripcion, rating, creado_en, clientes(nombre)')
        .eq('estado', estado)
        .order('creado_en', desc=True)
        .execute()
    )
    return respuesta.data

def eliminar_reseña(resena_id: int) -> None:
    existente = supabase.table('reseñas') \
        .select('reseña_id') \
        .eq('reseña_id', resena_id) \
        .execute()

    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.resena',
            message='Reseña no encontrada',
            description=f"No existe una reseña con id '{resena_id}'"
        ), 404)

    supabase.table('reseñas') \
        .delete() \
        .eq('reseña_id', resena_id) \
        .execute()
    
def crear_reseña(data: dict) -> dict:

    cliente = supabase.table('clientes') \
        .select('cliente_id') \
        .eq('email', data['email']) \
        .execute()

    if not cliente.data:
        raise ValueError(construir_error_api(
            code='not_found.cliente',
            message='Cliente no encontrado',
            description=f"No existe un cliente con el email '{data['email']}'"
        ), 404)

    cliente_id = cliente.data[0]['cliente_id']

    reserva = supabase.table('reservas') \
        .select('reserva_id') \
        .eq('cliente_id', cliente_id) \
        .eq('estado', 'confirmado') \
        .execute()

    if not reserva.data:
        raise ValueError(construir_error_api(
            code='forbidden.resena.sin_reserva',
            message='Sin reserva confirmada',
            description='Necesitás al menos una visita confirmada para dejar una reseña'
        ), 403)

    ya_reseño = supabase.table('reseñas') \
        .select('reseña_id') \
        .eq('cliente_id', cliente_id) \
        .execute()

    if ya_reseño.data:
        raise ValueError(construir_error_api(
            code='conflict.resena.duplicada',
            message='Ya existe una reseña',
            description='Ya dejaste una reseña anteriormente'
        ), 409)
    
    response = supabase.table('reseñas').insert({
        'cliente_id':  cliente_id,
        'rating':      data['rating'],
        'descripcion': data['descripcion'],
        'estado':      False,
        'creado_en':   a_utc(datetime.now()).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    }).execute()

    return response.data[0]


def actualizar_estado_reseña(reseña_id: int, nuevo_estado: bool) -> dict:
    existente = (
        supabase.table('reseñas')
        .select('reseña_id')
        .eq('reseña_id', reseña_id)
        .execute()
    )

    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.reseña',
            message="reseña no encontrada",
            description=f"No se encontró ningúna reseña con el ID {reseña_id}"
        ), 404)

    response = (
        supabase.table('reseñas')
        .update({'estado': nuevo_estado})
        .eq('reseña_id', reseña_id)
        .execute()
    )


    return response.data[0]