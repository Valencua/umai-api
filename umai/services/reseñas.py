from db import supabase
from datetime import datetime, timezone
from umai.utils import formatear_rfc3339

def crear_reseña(cliente_id, descripcion, rating):
    try:
        respuesta = (
            supabase.table('reseñas')
            .insert({
                'cliente_id': cliente_id,
                'descripcion': descripcion,
                'rating': rating,
                'estado': False,
                'creado_en': formatear_rfc3339(datetime.now(timezone.utc)).replace('+00:00', 'Z')
            })
            .execute()
        )
        return respuesta.data[0]
    except Exception as e:
        print(f"Error inesperado: {str(e)}")  
        return None  