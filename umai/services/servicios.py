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

def crear_servicio(data: dict) -> dict:
    existente = supabase.table('servicios') \
        .select('servicio_id') \
        .eq('nombre', data['nombre']) \
        .execute()
    if existente.data:
        raise ValueError(construir_error_api(
            code='conflict.nombre.duplicate',
            message="Nombre ya registrado",
            description=f"Ya existe un servicio con el nombre '{data['nombre']}'"
        ))
    response = supabase.table('servicios').insert({
        'nombre':      data['nombre'],
        'descripcion': data['descripcion'],
        'icono':       data['icono'],
        'estado':      data['estado']
    }).execute()

    return response.data[0]

def actualizar_estado_servicio(servicio_id: int, nuevo_estado: bool) -> dict:
    existente = (
        supabase.table('servicios')
        .select('servicio_id')
        .eq('servicio_id', servicio_id)
        .execute()
    )
        
    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.servicio',
            message="Servicio no encontrado",
            description=f"No se encontró ningún servicio con el ID {servicio_id}"
        ), 404)

    response = (
        supabase.table('servicios')
        .update({'estado': nuevo_estado})
        .eq('servicio_id', servicio_id)
        .execute()
    )


    return response.data[0]

