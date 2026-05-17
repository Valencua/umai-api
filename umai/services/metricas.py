from db import supabase
from datetime import datetime, timezone, timedelta
from umai.utils import a_utc, TZ_LOCAL

def obtener_reservas_hoy():
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

        # Consulta por rango: >= inicio del día (UTC) y < inicio del día siguiente (UTC)
        response = (
            supabase.from_('reservas')
            .select('*')
            .gte('fecha', inicio_iso)
            .lt('fecha', fin_iso)
            .execute()
        )

        return response.data
    except Exception:
        return None
