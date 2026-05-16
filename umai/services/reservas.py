import logging
from db import supabase

logger = logging.getLogger(__name__)

def traer_3_mas_recientes_reservas():
    try:
        reservas_recientes = (
        supabase.table('reservas')
        .select('*')
        .order('reserva_id', desc=True) # obtener los ultimos id creados, es decir, las reservas mas recientes
        .limit(3)
        .execute()
        )
        return reservas_recientes.data

    except Exception as e:
        logger.error(f"Error al traer reservas: {str(e)}", exc_info=True)
        return None
