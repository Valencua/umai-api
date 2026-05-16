from db.supabase_client import supabase
from umai.utils import construir_error_api

def actualizar_estado_servicio(servicio_id: int, nuevo_estado: bool) -> dict:
    existente = supabase.table('servicios')
        .select('servicio_id')
        .eq('servicio_id', servicio_id)
        .execute()
        
    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.servicio',
            message="Servicio no encontrado",
            description=f"No se encontró ningún servicio con el ID {servicio_id}"
        ), 404)

    response = supabase.table('servicios')
        .update({'estado': nuevo_estado})
        .eq('servicio_id', servicio_id)
        .execute()

    return response.data[0]