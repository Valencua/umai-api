from db.supabase_client import supabase
from datetime import datetime, timezone
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
    hoy = a_utc(datetime.now()).date().isoformat()
    response = supabase.table('reservas') \
        .select('reserva_id') \
        .eq('estado', 'cancelado') \
        .eq('fecha', hoy) \
        .execute()

    return {'cancelaciones': len(response.data)}