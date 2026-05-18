import logging
from db import supabase
from umai.constants import FORMATO_FECHA
from umai.utils import validar_email, validar_formato_fecha


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

        if str(fecha_reserva).startswith(fecha_busqueda) and estado_reserva == 'confirmado':
            return True

    return False
