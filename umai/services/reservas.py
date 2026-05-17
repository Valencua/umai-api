from db.supabase_client import supabase

def obtener_reservas_codigo(uuid_codigo):

    respuesta = supabase.table('reservas').select('*,cliente(*)').eq('uuid_codigo', codigo_buscado).execute()

    if len(respuesta) > 0:
        return respuesta.data[0]
    
    return None