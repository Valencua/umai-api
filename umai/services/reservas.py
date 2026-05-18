from datetime import datetime, timezone
from db import supabase

from umai.constants import (
    CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO,
    ESTADO_RESERVA_CANCELADO
)

from umai.utils import (
    construir_error_api,
    a_utc,
    TZ_LOCAL
)

HORARIOS_DISPONIBLES = [
    '20:00','21:00','22:00','23:00'
]

def obtener_disponibilidad(fecha: str):
    try:
        fecha_obj = datetime.strptime(
            fecha, '%Y-%m-%d'
            ).date()
        
    except ValueError:

            raise ValueError(construir_error_api(
                code='invalid.fecha',
                message='Fecha inválida',
                description='La fecha debe tener formato YYYY-MM-DD'
            ))

    hoy = datetime.now(timezone.utc).date()

    if fecha_obj < hoy:

        raise ValueError(construir_error_api(
            code='invalid.fecha.pasada',
            message='Fecha inválida',
            description='No se puede consultar disponibilidad para fechas pasadas'
        ))
    disponibilidad = []

    for horario in HORARIOS_DISPONIBLES:

         fecha_local = datetime.strptime(
         f'{fecha} {horario}',
         '%Y-%m-%d %H:%M'
         ).replace(tzinfo=TZ_LOCAL)

         fecha_utc = a_utc(fecha_local)
        
        fecha_hora = fecha_utc.isoformat().replace(
            '+00:00',
            'Z'
        )
        
         response = (
              supabase
              .table('reservas')
              .select('cantidad_personas')
              .select('cantidad_personas')
              .eq('fecha', fecha_hora)
              .neq('estado', ESTADO_RESERVA_CANCELADO)
              .execute()
        )
         
    personas_reservadas = sum(
            reserva['cantidad_personas']
            for reserva in response.data
        )
    
    lugares_disponibles = (
            CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO - personas_reservadas
        )
    
    disponibilidad.append({
            'horario': horario,
            'lugares_disponibles': lugares_disponibles,
            'disponible': lugares_disponibles > 0
        })
    return disponibilidad
