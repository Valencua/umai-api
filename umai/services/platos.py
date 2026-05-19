import uuid

from db import supabase

from umai.constants import (
    ERROR_CODE_ETIQUETAS_INVALIDAS,
    ERROR_CODE_PLATO_DUPLICADO
)

from umai.utils import construir_error_api


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
