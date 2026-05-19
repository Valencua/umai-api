from db import supabase
from datetime import datetime

from umai.utils import a_local

def obtener_reservas():
    reservas = (
        supabase.table('reservas')
        .select('*')
        .order('reserva_id', desc=True)
        .execute()
    )

    for reserva in reservas.data:
        fecha = reserva.get('fecha')
        
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))

        if isinstance(fecha, datetime):
            reserva['fecha'] = a_local(fecha)

    return reservas.data