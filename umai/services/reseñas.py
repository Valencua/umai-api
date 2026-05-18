from db.supabase_client import supabase
from umai.utils import construir_error_api

def actualizar_estado_reseña(reseña_id: int, nuevo_estado: bool) -> dict:
    existente = (
        supabase.table('reseñas')
        .select('reseña_id')
        .eq('reseña_id', reseña_id)
        .execute()
    )
        
    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.reseña',
            message="reseña no encontrada",
            description=f"No se encontró ningúna reseña con el ID {reseña_id}"
        ), 404)

    response = (
        supabase.table('reseñas')
        .update({'estado': nuevo_estado})
        .eq('reseña_id', reseña_id)
        .execute()
    )


    return response.data[0]