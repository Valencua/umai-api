from db.supabase_client import supabase
from datetime import datetime, timedelta
from umai.utils import a_utc
def obtener_rating_promedio() -> dict:
    response = supabase.table('reseñas') \
        .select('rating') \
        .eq('estado', True) \
        .execute()

    reseñas = response.data

    if not reseñas:
        return {'promedio': 0}

    promedio = round(sum(r['rating'] for r in reseñas) / len(reseñas), 1)

    return {'promedio': promedio}

def obtener_cancelaciones_hoy() -> dict:
    ahora = a_utc(datetime.now())
    inicio_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia    = inicio_dia + timedelta(days=1)

    response = supabase.table('reservas') \
        .select('reserva_id') \
        .eq('estado', 'cancelado') \
        .gte('fecha', inicio_dia.isoformat()) \
        .lt('fecha', fin_dia.isoformat()) \
        .execute()

    return {'cancelaciones': len(response.data)}