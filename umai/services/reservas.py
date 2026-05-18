from db import supabase

def get_top3_reservas():
    reservas_recientes = (
        supabase.table('reservas')
        .select('*')
        .order('reserva_id', desc=True) # obtener los ultimos id creados, es decir, las reservas mas recientes
        .limit(3)
        .execute()
    )
    return reservas_recientes.data
