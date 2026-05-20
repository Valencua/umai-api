
from db import supabase
from datetime import datetime, timezone, timedelta
from umai.utils import a_utc, TZ_LOCAL, a_local
from umai.constants import ESTADO_RESERVA_PENDIENTE, ESTADO_RESERVA_CONFIRMADO, FORMATO_FECHA

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

def obtener_reservas_hoy():
    ahora = datetime.now(TZ_LOCAL)
    inicio_dia_local = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia_local    = inicio_dia_local + timedelta(days=1)

    inicio_utc = a_utc(inicio_dia_local).isoformat().replace('+00:00', 'Z')
    fin_utc    = a_utc(fin_dia_local).isoformat().replace('+00:00', 'Z')

    response = (
        supabase.from_('reservas')
        .select('*')
        .gte('fecha', inicio_utc)
        .lt('fecha', fin_utc)
        .execute()
    )
    return {'reservas': len(response.data)}

def obtener_cancelaciones_hoy() -> dict:
    ahora = datetime.now(TZ_LOCAL)
    inicio_dia_local = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia_local    = inicio_dia_local + timedelta(days=1)

    inicio_utc = a_utc(inicio_dia_local).isoformat().replace('+00:00', 'Z')
    fin_utc    = a_utc(fin_dia_local).isoformat().replace('+00:00', 'Z')
    response = supabase.table('reservas') \
        .select('reserva_id') \
        .eq('estado', 'cancelado') \
        .gte('fecha', inicio_utc) \
        .lt('fecha', fin_utc) \
        .execute()

    return {'cancelaciones': len(response.data)}

def obtener_metricas_reservas() -> dict:
    response = (
        supabase.table('reservas')
        .select('estado')
        .execute()
    )

    reservas = response.data

    if not reservas:
        return {
            'total': 0,
            'visitaron':  {'cantidad': 0, 'porcentaje': 0},
            'canceladas': {'cantidad': 0, 'porcentaje': 0},
            'pendiente':    {'cantidad': 0, 'porcentaje': 0}
        }

    total      = len(reservas)
    visitaron  = sum(1 for r in reservas if r['estado'] == 'confirmado')
    canceladas = sum(1 for r in reservas if r['estado'] == 'cancelado')
    pendiente    = sum(1 for r in reservas if r['estado'] == 'pendiente')

    def porcentaje(cantidad):
        return round(cantidad / total * 100)

    return {
        'total': total,
        'visitaron':  {'cantidad': visitaron,  'porcentaje': porcentaje(visitaron)},
        'canceladas': {'cantidad': canceladas, 'porcentaje': porcentaje(canceladas)},
        'pendientes':    {'cantidad': pendiente,    'porcentaje': porcentaje(pendiente)}
    }

def obtener_personas_hoy():
    try:
        ahora = datetime.now(TZ_LOCAL)
        inicio_dia_local = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia_local    = inicio_dia_local + timedelta(days=1)

        inicio_utc = a_utc(inicio_dia_local).isoformat().replace('+00:00', 'Z')
        fin_utc    = a_utc(fin_dia_local).isoformat().replace('+00:00', 'Z')

        response = (
            supabase.from_('reservas')
            .select('cantidad_personas')
            .gte('fecha', inicio_utc)
            .lt('fecha', fin_utc)
            .eq('estado', ESTADO_RESERVA_CONFIRMADO)
            .execute()
        )
        personas_hoy = 0
        for reserva in response.data:
            personas_hoy += reserva['cantidad_personas']
        
        return {'personas': personas_hoy}
    except Exception:
        return None

DIAS_SEMANA = {
    'Monday':    'Lunes',
    'Tuesday':   'Martes',
    'Wednesday': 'Miércoles',
    'Thursday':  'Jueves',
    'Friday':    'Viernes',
    'Saturday':  'Sábado',
    'Sunday':    'Domingo'
}

