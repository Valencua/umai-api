from db.supabase_client import supabase

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

def obtener_metricas_reservas() -> dict:
    response = supabase.table('reservas').select('estado').execute()

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