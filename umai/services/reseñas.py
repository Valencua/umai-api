from db import supabase
from datetime import datetime
from umai.utils import a_utc, validar_email, validar_formato_fecha, construir_error_api, TZ_LOCAL
from umai.constants import FORMATO_FECHA, ESTADO_RESERVA_CONFIRMADO
from umai.validators.reseñas import validar_existe_cliente, cliente_tiene_reservas_confirmadas, cliente_tiene_reseña


def validar_usuario_para_reseña(email):
    email_validado = validar_email(email)
    cliente_body = validar_existe_cliente(email_validado)
    if not cliente_body:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'usuario_no_encontrado'
        }

    cliente_id = cliente_body.get('cliente_id')
    reservas_resp = cliente_tiene_reservas_confirmadas(cliente_id)
    # ¿Tiene reservas confirmadas?
    if not reservas_resp.data:
        return {
            'puede_realizar_reseña': False,
            'motivo': 'sin_reservas_confirmadas'
        }
    #...tiene reservas confirmadas, ahora validar si ya tiene una reseña o no
    # ¿Ya tiene una reseña?
    reseñas_resp = cliente_tiene_reseña(cliente_id)
    
    if reseñas_resp.data: #si tiene data, puede editarlo
        return {
            'puede_realizar_reseña': True,
            'motivo': 'puede_editar_reseña_existente'
        }
    #sino, se deberia crear la reseña
    return {
        'puede_realizar_reseña': True,
        'motivo': 'puede_crear_reseña'
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

