from db import supabase
from datetime import datetime
from umai.utils import a_utc, validar_email, validar_formato_fecha, construir_error_api, TZ_LOCAL
from umai.constants import FORMATO_FECHA, ESTADO_RESERVA_CONFIRMADO


def validar_usuario_para_reseña(email, fecha):
    email_validado = validar_email(email)
    fecha_validada = validar_formato_fecha(fecha, FORMATO_FECHA)
    
    # Convertir fecha local a UTC para comparar con BD
    fecha_dt_local = datetime.combine(fecha_validada.date(), datetime.min.time(), tzinfo=TZ_LOCAL)
    fecha_utc = a_utc(fecha_dt_local)
    fecha_utc_str = fecha_utc.isoformat().replace('+00:00', 'Z')[:10]  # Obtener solo la parte de fecha en UTC

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

    reseñas_resp = (
        supabase.table('reseñas')
        .select('reseña_id', count='exact')
        .eq('cliente_id', cliente_id)
        .execute()
    )
    cantidad_reseñas = len(reseñas_resp.data)

    # Contar reservas confirmadas del cliente
    reservas_resp = (
        supabase.table('reservas')
        .select('fecha', 'estado', count='exact')
        .eq('cliente_id', cliente_id)
        .eq('estado', ESTADO_RESERVA_CONFIRMADO)
        .execute()
    )
    cantidad_reservas = len(reservas_resp.data)

    # si no tiene reservas directamente....
    if not reservas_resp or not reservas_resp.data:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'sin_reservas_confirmadas'
        }

    if cantidad_reseñas >= cantidad_reservas:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'reseña_existente'
        }

    fecha_encontrada = False
    for reserva in reservas_resp.data:
        fecha_reserva = reserva.get('fecha')
        if fecha_reserva and str(fecha_reserva).startswith(fecha_utc_str):
            fecha_encontrada = True
            break
    if not fecha_encontrada:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'sin_reservas_confirmadas'
        }
    return {
        'puede_realizar_reseña': True,
        'motivo': None
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

