from datetime import datetime, timedelta

from db.connection import fetch_all
from umai.constants import (
    DIAS_SEMANA,
    ESTADO_RESERVA_CANCELADO,
    ESTADO_RESERVA_CONFIRMADO,
    ESTADO_RESERVA_PENDIENTE,
    FORMATO_FECHA_STR_Z,
)
from umai.utils import TZ_LOCAL, a_utc


def _rango_utc_dia(dia) -> tuple[str, str]:
    inicio_local = datetime.combine(dia, datetime.min.time(), tzinfo=TZ_LOCAL)
    fin_local = inicio_local + timedelta(days=1)
    inicio_utc = a_utc(inicio_local).strftime(FORMATO_FECHA_STR_Z)
    fin_utc = a_utc(fin_local).strftime(FORMATO_FECHA_STR_Z)
    return inicio_utc, fin_utc


def obtener_rating_promedio() -> dict:
    rows = fetch_all(
        """
        SELECT rating
        FROM reseñas
        WHERE estado = true
        """
    )
    if not rows:
        return {'promedio': 0}
    promedio = round(sum(r['rating'] for r in rows) / len(rows), 1)
    return {'promedio': promedio}


def obtener_reservas_hoy() -> dict:
    inicio_iso, fin_iso = _rango_utc_dia(datetime.now(TZ_LOCAL).date())
    rows = fetch_all(
        """
        SELECT reserva_id
        FROM reservas
        WHERE fecha >= %s AND fecha < %s
        """,
        (inicio_iso, fin_iso),
    )
    return {'reservas_hoy': len(rows)}


def obtener_cancelaciones_hoy() -> dict:
    inicio_iso, fin_iso = _rango_utc_dia(datetime.now(TZ_LOCAL).date())
    rows = fetch_all(
        """
        SELECT reserva_id
        FROM reservas
        WHERE estado = %s AND fecha >= %s AND fecha < %s
        """,
        (ESTADO_RESERVA_CANCELADO, inicio_iso, fin_iso),
    )
    return {'cancelaciones': len(rows)}


def obtener_metricas_reservas() -> dict:
    rows = fetch_all("SELECT estado FROM reservas")

    vacio = {
        'total': 0,
        'visitaron': {'cantidad': 0, 'porcentaje': 0},
        'canceladas': {'cantidad': 0, 'porcentaje': 0},
        'pendientes': {'cantidad': 0, 'porcentaje': 0},
    }
    if not rows:
        return vacio

    total = len(rows)
    visitaron = sum(1 for r in rows if r['estado']  == ESTADO_RESERVA_CONFIRMADO)
    canceladas = sum(1 for r in rows if r['estado'] == ESTADO_RESERVA_CANCELADO)
    pendientes = sum(1 for r in rows if r['estado'] == ESTADO_RESERVA_PENDIENTE)

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
        rows = fetch_all(
            """
            SELECT reserva_id
            FROM reservas
            WHERE fecha >= %s AND fecha < %s
            """,
            (inicio_iso, fin_iso),
        )
        resultado.append({
            'dia': DIAS_SEMANA[dia_local.strftime('%A')],
            'reservas': len(rows),
        })

    return resultado


def obtener_personas_hoy() -> dict:
    inicio_iso, fin_iso = _rango_utc_dia(datetime.now(TZ_LOCAL).date())
    rows = fetch_all(
        """
        SELECT cantidad_personas
        FROM reservas
        WHERE fecha >= %s AND fecha < %s AND estado = %s
        """,
        (inicio_iso, fin_iso, ESTADO_RESERVA_CONFIRMADO),
    )
    personas_hoy = sum(r['cantidad_personas'] for r in rows)
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