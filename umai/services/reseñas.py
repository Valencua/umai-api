from db import supabase
from umai.constants import FORMATO_FECHA
from umai.utils import validar_email, validar_formato_fecha


def validar_usuario_para_reseña(email, fecha):
    validar_email(email)
    fecha_validada = validar_formato_fecha(fecha, FORMATO_FECHA)
    fecha_normalizada = fecha_validada.strftime(FORMATO_FECHA)

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
        .select('fecha')
        .eq('cliente_id', cliente_id)
        .execute()
    )
    return any(str(reserva.get('fecha')).startswith(fecha_normalizada) for reserva in reservas_resp.data)

