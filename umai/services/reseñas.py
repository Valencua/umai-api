import logging
from db import supabase
from datetime import datetime, timezone
from umai.utils import formatear_rfc3339, a_utc

logger = logging.getLogger(__name__
)
def crear_reseña(data: dict):
    respuesta = (
        supabase.table('reseñas')
        .insert({
            'cliente_id': data['cliente_id'],
            'descripcion': data['descripcion'],
            'rating': data['rating'],
            'estado': False,
            'creado_en': a_utc(datetime.now()).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        })
        .execute()
    )
    return respuesta.data[0]