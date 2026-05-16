
import logging
from db import supabase


def validar_usuario_para_reseña(email, fecha):
    try:
        # Buscar cliente por email, si existe una reserva siquiera
        cliente_resp = (
            supabase.table('clientes')
            .select('cliente_id')
            .eq('email', email)
            .limit(1)
            .execute()
        )

        # si el data está vacio quiere decir que no se encontró cliente con ese email
        if not cliente_resp.data:
            return False

        cliente_id = cliente_resp.data[0].get('cliente_id')

        # Buscar reservas del cliente
        reservas_resp = (
            supabase.table('reservas')
            .select('fecha')
            .eq('cliente_id', cliente_id)
            .execute()
        )

        # Chequear si alguna fecha empieza con la fecha buscada. any() te ahorras el loop explícito y es más eficiente.
        return any(str(r.get('fecha')).startswith(str(fecha)) for r in reservas_resp.data)

    except Exception:
        return None
