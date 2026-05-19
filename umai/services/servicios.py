from db.supabase_client import supabase
from umai.utils import construir_error_api

def obtener_servicios() -> list:
    response = (
        supabase.table('servicios')
        .select('*')
        .execute()
    )

    if not response.data:
        raise ValueError(construir_error_api(
            code='not_found.servicios.empty',
            message="No se encontraron servicios",
            description="No existen servicios registrados en la base de datos actualmente."
        ))
        
    return response.data
