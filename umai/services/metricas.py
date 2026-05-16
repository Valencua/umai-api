import logging
from db import supabase
from datetime import datetime

def obtener_reservas_hoy():
    try:
        fecha_hoy = datetime.now().date()

        response = (
            supabase.from_('reservas')
            .select('*')
            .eq('fecha', str(fecha_hoy))
            .execute()
        )

        if response.status_code == 200:
            reservas = response.data
            return reservas
        else:
            return []
    except Exception as e:
        logging.error(f"Excepción al obtener reservas: {e}")
        return []