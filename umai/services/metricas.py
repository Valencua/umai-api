
from db import supabase
from datetime import datetime, timedelta
from umai.utils import a_utc, TZ_LOCAL
from umai.constants import ESTADO_RESERVA_CONFIRMADO, DIAS_SEMANA, FORMATO_FECHA_STR_Z, ESTADO_RESERVA_CANCELADO, ESTADO_RESERVA_PENDIENTE

def _rango_utc_dia(dia) -> tuple[str, str]:
    inicio_local = datetime.combine(dia, datetime.min.time(), tzinfo=TZ_LOCAL)
    fin_local = inicio_local + timedelta(days=1)
    inicio_utc = a_utc(inicio_local).strftime(FORMATO_FECHA_STR_Z)
    fin_utc = a_utc(fin_local).strftime(FORMATO_FECHA_STR_Z)
    return inicio_utc, fin_utc

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

def obtener_reservas_hoy() -> dict:
    inicio_iso, fin_iso = _rango_utc_dia(datetime.now(TZ_LOCAL).date())
    response = (
        supabase.table('reservas')
        .select('reserva_id')
        .gte('fecha', inicio_iso)
        .lt('fecha', fin_iso)
        .execute()
    )
    return {'reservas_hoy': len(response.data)}

def obtener_cancelaciones_hoy() -> dict:
    inicio_iso, fin_iso = _rango_utc_dia(datetime.now(TZ_LOCAL).date())
    response = supabase.table('reservas') \
        .select('reserva_id') \
        .eq('estado', ESTADO_RESERVA_CANCELADO) \
        .gte('fecha', inicio_iso) \
        .lt('fecha', fin_iso) \
        .execute()
    return {'cancelaciones': len(response.data)}

def obtener_metricas_reservas() -> dict:
    response = (
        supabase.table('reservas')
        .select('estado')
        .execute()
    )
    reservas = response.data
    vacio = {
        'total': 0,
        'visitaron': {'cantidad': 0, 'porcentaje': 0},
        'canceladas': {'cantidad': 0, 'porcentaje': 0},
        'pendientes': {'cantidad': 0, 'porcentaje': 0},
    }
    if not reservas:
        return vacio
    total = len(reservas) 
    visitaron = sum(1 for r in reservas if r['estado'] == ESTADO_RESERVA_CONFIRMADO)
    canceladas = sum(1 for r in reservas if r['estado'] == ESTADO_RESERVA_CANCELADO)
    pendientes = sum(1 for r in reservas if r['estado'] == ESTADO_RESERVA_PENDIENTE)
    def porcentaje(cantidad: int) -> int:
        return round(cantidad / total * 100)
    return {
        'total': total,
        'visitaron': {'cantidad': visitaron, 'porcentaje': porcentaje(visitaron)},
        'canceladas': {'cantidad': canceladas, 'porcentaje': porcentaje(canceladas)},
        'pendientes': {'cantidad': pendientes, 'porcentaje': porcentaje(pendientes)},
    }

def obtener_reservas_ultimos_7_dias() -> list:
    hoy_local = datetime.now(TZ_LOCAL).date()
    resultado = []
    for i in range(6, -1, -1):
        dia_local = hoy_local - timedelta(days=i)
        inicio_iso, fin_iso = _rango_utc_dia(dia_local)
        response = supabase.table('reservas') \
            .select('reserva_id') \
            .gte('fecha', inicio_iso) \
            .lt('fecha', fin_iso) \
            .execute()
        resultado.append({
            'dia': DIAS_SEMANA[dia_local.strftime('%A')],
            'reservas': len(response.data),
        })
    return resultado

def obtener_personas_hoy() -> dict:
    inicio_iso, fin_iso = _rango_utc_dia(datetime.now(TZ_LOCAL).date())
    response = (
        supabase.table('reservas')
        .select('cantidad_personas')
        .gte('fecha', inicio_iso)
        .lt('fecha', fin_iso)
        .eq('estado', ESTADO_RESERVA_CONFIRMADO)
        .execute()
    )
    personas_hoy = sum(r['cantidad_personas'] for r in response.data)
    return {'personas_hoy': personas_hoy}

def obtener_dashboard() -> dict:
    return {
        'rating': obtener_rating_promedio(),
        'reservas_hoy': obtener_reservas_hoy(),
        'cancelaciones': obtener_cancelaciones_hoy(),
        'metricas_reservas': obtener_metricas_reservas(),
        'personas_hoy': obtener_personas_hoy(),
        'reservas_semana': obtener_reservas_ultimos_7_dias(),
    }
