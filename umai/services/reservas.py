from db import supabase
from datetime import datetime
from umai.constants import FORMATO_FECHA, FORMATO_HORARIO
from umai.utils import a_local, formatear_rfc3339  

def get_top3_reservas():
    reservas_recientes = (
        supabase.table('reservas')
        .select('*')
        .order('reserva_id', desc=True)
        .limit(3)
        .execute()
    )

    for reserva in reservas_recientes.data:
        fecha = reserva.get('fecha')
        
        if fecha:
            if isinstance(fecha, str):
                fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            else:
                fecha_dt = fecha
            fecha_local = a_local(fecha_dt)
            reserva['fecha'] = formatear_rfc3339(fecha_local)
            reserva['fecha'] = fecha_local.strftime(f"{FORMATO_FECHA} {FORMATO_HORARIO}")

    return reservas_recientes.data