import logging
from db import supabase

logger = logging.getLogger(__name__)

def listar_reseñas(estado: bool)-> list:
    respuesta = (
        supabase.table('reseñas')
        .select('reseña_id, descripcion, rating, creado_en, clientes(nombre)')
        .eq('estado', estado)
        .order('creado_en', desc=True)
        .execute()
    )
    return respuesta.data