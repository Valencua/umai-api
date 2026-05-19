from db.supabase_client import supabase
from datetime import datetime, timedelta, timezone
from umai.constants import ESTADO_RESERVA_CONFIRMADO, FORMATO_FECHA
from umai.validators import reservas

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

def obtener_reservas_semanal() -> list:
    hoy = datetime.now(timezone.utc)
    hace_siete_dias = hoy - timedelta(days=7)

    hoy_str = hoy.strftime(FORMATO_FECHA)
    hace_siete_dias_str = hace_siete_dias.strftime(FORMATO_FECHA)

    response = (
        supabase.table('reservas') 
        .select('*') 
        .eq('estado', ESTADO_RESERVA_CONFIRMADO) 
        .gte('fecha', hace_siete_dias_str) 
        .lte('fecha', hoy_str)
        .execute()
    )

    return response.data if response.data else []