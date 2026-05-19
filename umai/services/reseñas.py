<<<<<<< HEAD
from db import supabase
from datetime import datetime, timezone
from umai.utils import formatear_rfc3339, a_utc, validar_email, validar_formato_fecha
from umai.constants import FORMATO_FECHA, ESTADO_RESERVA_CONFIRMADO


def validar_usuario_para_reseña(email, fecha):
    email = validar_email(email)
    fecha_validada = validar_formato_fecha(fecha, FORMATO_FECHA)
    fecha_busqueda = fecha_validada.strftime(FORMATO_FECHA)

    cliente_resp = (
        supabase.table('clientes')
        .select('cliente_id')
        .eq('email', email)
        .limit(1)
        .execute()
    )

    if not cliente_resp.data:
        return False

    cliente_id = cliente_resp.data[0].get('cliente_id')

    reservas_resp = (
        supabase.table('reservas')
        .select('fecha', 'estado')
        .eq('cliente_id', cliente_id)
        .execute()
    )

    for reserva in reservas_resp.data:
        fecha_reserva = reserva.get('fecha')
        estado_reserva = reserva.get('estado')

        if str(fecha_reserva).startswith(fecha_busqueda) and estado_reserva == ESTADO_RESERVA_CONFIRMADO:
            return True

    return False

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

