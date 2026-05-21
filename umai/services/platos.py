from db import supabase
import uuid
from umai.utils import construir_error_api

from umai.constants import (
    ERROR_CODE_ETIQUETAS_INVALIDAS,
    ERROR_CODE_PLATO_DUPLICADO
)


def crear_plato(data: dict) -> dict:

    existente = (
        supabase
        .table('platos')
        .select('plato_id')
        .eq('nombre', data['nombre'])
        .execute()
    )

    if existente.data:

        raise ValueError(construir_error_api(
            code=ERROR_CODE_PLATO_DUPLICADO,
            message='Plato ya existente',
            description=f"Ya existe un plato con el nombre '{data['nombre']}'"
        ))

    etiquetas = data.get('etiquetas', [])

    if etiquetas:

        etiquetas_existentes = (
            supabase
            .table('etiquetas')
            .select('etiqueta_id')
            .in_('etiqueta_id', etiquetas)
            .execute()
        )

        ids_existentes = [
            etiqueta['etiqueta_id']
            for etiqueta in etiquetas_existentes.data
        ]

        etiquetas_invalidas = [
            etiqueta_id
            for etiqueta_id in etiquetas
            if etiqueta_id not in ids_existentes
        ]

        if etiquetas_invalidas:

            raise ValueError(construir_error_api(
                code=ERROR_CODE_ETIQUETAS_INVALIDAS,
                message='Etiquetas inexistentes',
                description=f'Las siguientes etiquetas no existen: {etiquetas_invalidas}'
            ))

    foto = data['foto']

    extension = foto.filename.split('.')[-1]

    nombre_archivo = f'{uuid.uuid4()}.{extension}'

    contenido_imagen = foto.read()

    supabase.storage.from_('platos').upload(
        path=nombre_archivo,
        file=contenido_imagen,
        file_options={
            'content-type': foto.content_type
        }
    )

    foto_url = (
        supabase
        .storage
        .from_('platos')
        .get_public_url(nombre_archivo)
    )

    response = (
        supabase
        .table('platos')
        .insert({
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'precio': data['precio'],
            'foto': foto_url,
        })
        .execute()
    )

    plato = response.data[0]

    if etiquetas:

        relaciones = [
            {
                'plato_id': plato['plato_id'],
                'etiqueta_id': etiqueta_id,
            }
            for etiqueta_id in etiquetas
        ]

        (
            supabase
            .table('plato_etiquetas')
            .insert(relaciones)
            .execute()
        )

    return plato

def traer_todos_los_platos():
    platos_resp = (
        supabase.table('platos')
        .select('*')
        .execute()
    )
    return platos_resp.data
    
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
    

def actualizar_plato(plato_id: int, data: dict) -> dict:

    existente = supabase.table('platos') \
        .select('*') \
        .eq('plato_id', plato_id) \
        .execute()

    if not existente.data:
        raise ValueError(construir_error_api(
            code='not_found.plato',
            message='Plato no encontrado',
            description=f"No existe un plato con id '{plato_id}'"
        ), 404)

    plato_actual = existente.data[0]
    campos_actualizar = {}

    if 'nombre' in data:
        duplicado = supabase.table('platos') \
            .select('plato_id') \
            .eq('nombre', data['nombre']) \
            .neq('plato_id', plato_id) \
            .execute()
        if duplicado.data:
            raise ValueError(construir_error_api(
                code=ERROR_CODE_PLATO_DUPLICADO,
                message='Nombre ya existente',
                description=f"Ya existe un plato con el nombre '{data['nombre']}'"
            ))
        campos_actualizar['nombre'] = data['nombre']

    if 'descripcion' in data:
        campos_actualizar['descripcion'] = data['descripcion']

    if 'precio' in data:
        campos_actualizar['precio'] = data['precio']

    if 'foto' in data:
        foto = data['foto']

        foto_vieja = plato_actual['foto']
        if foto_vieja:
            path_viejo = foto_vieja.split('/platos/')[-1]
            supabase.storage.from_('platos').remove([path_viejo])

        extension = foto.filename.split('.')[-1]
        nombre_archivo = f'{uuid.uuid4()}.{extension}'
        supabase.storage.from_('platos').upload(
            path=nombre_archivo,
            file=foto.read(),
            file_options={'content-type': foto.content_type}
        )
        campos_actualizar['foto'] = supabase.storage.from_('platos').get_public_url(nombre_archivo)

    if 'etiquetas' in data:
        etiquetas = data['etiquetas']

        etiquetas_existentes = supabase.table('etiquetas') \
            .select('etiqueta_id') \
            .in_('etiqueta_id', etiquetas) \
            .execute()

        ids_existentes = [e['etiqueta_id'] for e in etiquetas_existentes.data]
        etiquetas_invalidas = [e for e in etiquetas if e not in ids_existentes]

        if etiquetas_invalidas:
            raise ValueError(construir_error_api(
                code=ERROR_CODE_ETIQUETAS_INVALIDAS,
                message='Etiquetas inexistentes',
                description=f'Las siguientes etiquetas no existen: {etiquetas_invalidas}'
            ))

        supabase.table('plato_etiquetas') \
            .delete() \
            .eq('plato_id', plato_id) \
            .execute()

        if etiquetas:
            relaciones = [{'plato_id': plato_id, 'etiqueta_id': e} for e in etiquetas]
            supabase.table('plato_etiquetas').insert(relaciones).execute()

    response = supabase.table('platos') \
        .update(campos_actualizar) \
        .eq('plato_id', plato_id) \
        .execute()

    return response.data[0]