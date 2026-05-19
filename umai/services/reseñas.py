from db import supabase
from datetime import datetime
from umai.utils import a_utc, validar_email, validar_formato_fecha, construir_error_api
from umai.constants import FORMATO_FECHA, ESTADO_RESERVA_CONFIRMADO


def validar_usuario_para_reseña(email, fecha):
    email_validado = validar_email(email)
    fecha_validada = validar_formato_fecha(fecha, FORMATO_FECHA)
    fecha_busqueda = fecha_validada.strftime(FORMATO_FECHA)

    cliente_resp = (
        supabase.table('clientes')
        .select('cliente_id')
        .eq('email', email_validado)
        .limit(1)
        .execute()
    )

    if not cliente_resp.data:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'usuario_no_encontrado'
        }

    cliente_id = cliente_resp.data[0].get('cliente_id')

    reseñas_iguales = (
        supabase.table('reseñas')
        .select('reseña_id')
        .eq('cliente_id', cliente_id)
        .eq('fecha', fecha_busqueda)
        .limit(1)
        .execute()
    )

    if reseñas_iguales.data:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'reseña_existente'
        }

    reservas_resp = (
        supabase.table('reservas')
        .select('fecha', 'estado')
        .eq('cliente_id', cliente_id)
        .eq('estado', ESTADO_RESERVA_CONFIRMADO)
        .execute()
    )

    if not reservas_resp or not reservas_resp.data:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'sin_reservas_confirmadas'
        }

    for reserva in reservas_resp.data:
        fecha_reserva = reserva.get('fecha')

        if str(fecha_reserva).startswith(fecha_busqueda):
            return {
                'puede_realizar_reseña': True,
                'motivo': None
            }

    return {
        'puede_realizar_reseña': False,
        'motivo': 'sin_reservas_confirmadas'
    }

def listar_reseñas(estado: bool)-> list:
    respuesta = (
        supabase.table('reseñas')
        .select('reseña_id, descripcion, rating, creado_en, clientes(nombre)')
        .eq('estado', estado)
        .order('creado_en', desc=True)
        .execute()
    )
    return respuesta.data

def eliminar_reseña(reseña_id: int):
    try:
        respuesta = (supabase.table('reseñas').delete().eq('reseña_id', reseña_id).execute())

        if not respuesta.data:
            return False
        
        return True
    
    except Exception as e:
        print(f"Error al eliminar reseña: {str(e)}")
        return None

def crear_reseña(data: dict):
    respuesta = (
        supabase.table('reseñas')
        .insert({
            'cliente_id': data['cliente_id'],
            'descripcion': data['descripcion'],
            'rating': data['rating'],
            'estado': False,
            'creado_en': a_utc(datetime.now()).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        })
        .execute()
    )
    return respuesta.data[0]

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

