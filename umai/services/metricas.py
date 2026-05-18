from db import supabase
from datetime import datetime, timedelta
from umai.utils import a_utc, TZ_LOCAL
from umai.constants import ESTADO_RESERVA_PENDIENTE

def obtener_personas_hoy():
    try:
        fecha_hoy_local = datetime.now(TZ_LOCAL).date()
        inicio_local = datetime.combine(fecha_hoy_local, datetime.min.time(), tzinfo=TZ_LOCAL)
        fin_local = datetime.combine(fecha_hoy_local + timedelta(days=1), datetime.min.time(), tzinfo=TZ_LOCAL)

        # convertir a UTC
        inicio_utc = a_utc(inicio_local)
        fin_utc = a_utc(fin_local)
        # Usamos el sufijo 'Z' para indicar UTC de forma compacta
        inicio_iso = inicio_utc.isoformat().replace('+00:00', 'Z')
        fin_iso = fin_utc.isoformat().replace('+00:00', 'Z')

        response = (
            supabase.from_('reservas')
            .select('cantidad_personas')
            .gte('fecha', inicio_iso)
            .lt('fecha', fin_iso)
            .eq('estado', ESTADO_RESERVA_PENDIENTE)
            .execute()
        )
        personas_hoy = 0
        for reserva in response.data:
            personas_hoy += reserva['cantidad_personas']

        return personas_hoy
    except Exception:
        return None

