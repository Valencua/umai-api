from db import supabase
from umai.utils import construir_error_api

def eliminar_plato(plato_id: int) -> None:

    existente = supabase.table('platos') \
        .select('plato_id, foto') \
        .eq('plato_id', plato_id) \
        .execute()

    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.plato',
            message='Plato no encontrado',
            description=f"No existe un plato con id '{plato_id}'"
        ), 404)

    foto_url = existente.data[0]['foto']
    if foto_url:
        path = foto_url.split('/platos/')[-1]
        supabase.storage.from_('platos').remove([path])

    supabase.table('plato_etiquetas') \
        .delete() \
        .eq('plato_id', plato_id) \
        .execute()

    supabase.table('platos') \
        .delete() \
        .eq('plato_id', plato_id) \
        .execute()