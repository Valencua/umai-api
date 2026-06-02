from db import supabase
from db.connection import execute, fetch_all, fetch_one
import uuid

from umai.utils import construir_error_api
from umai.constants import (
    ERROR_CODE_ETIQUETAS_INVALIDAS,
    ERROR_CODE_PLATO_DUPLICADO,
)


def _validar_etiquetas_ids(etiquetas: list) -> None:
    if not etiquetas:
        return

    placeholders = ','.join(['%s'] * len(etiquetas))
    rows = fetch_all(
        f"""
        SELECT etiqueta_id
        FROM etiquetas
        WHERE etiqueta_id IN ({placeholders})
        """,
        tuple(etiquetas),
    )

    ids_existentes = [row['etiqueta_id'] for row in rows]
    etiquetas_invalidas = [
        etiqueta_id for etiqueta_id in etiquetas
        if etiqueta_id not in ids_existentes
    ]

    if etiquetas_invalidas:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_ETIQUETAS_INVALIDAS,
            message='Etiquetas inexistentes',
            description=f'Las siguientes etiquetas no existen: {etiquetas_invalidas}'
        ))


def _insertar_plato_etiquetas(plato_id: int, etiquetas: list) -> None:
    for etiqueta_id in etiquetas:
        execute(
            """
            INSERT INTO plato_etiquetas (plato_id, etiqueta_id)
            VALUES (%s, %s)
            """,
            (plato_id, etiqueta_id),
        )


def crear_plato(data: dict) -> dict:
    existente = fetch_one(
        """
        SELECT plato_id
        FROM platos
        WHERE nombre = %s
        """,
        (data['nombre'],),
    )

    if existente:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_PLATO_DUPLICADO,
            message='Plato ya existente',
            description=f"Ya existe un plato con el nombre '{data['nombre']}'"
        ))

    etiquetas = data.get('etiquetas', [])
    _validar_etiquetas_ids(etiquetas)

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

    plato = execute(
        """
        INSERT INTO platos (nombre, descripcion, precio, foto)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (
            data['nombre'],
            data['descripcion'],
            data['precio'],
            foto_url,
        ),
        returning=True,
    )

    plato = dict(plato)

    if etiquetas:
        _insertar_plato_etiquetas(plato['plato_id'], etiquetas)

    return plato


def _agrupar_etiquetas_por_plato(plato_ids: list) -> dict:
    if not plato_ids:
        return {}

    placeholders = ','.join(['%s'] * len(plato_ids))
    rows = fetch_all(
        f"""
        SELECT plato_id, etiqueta_id
        FROM plato_etiquetas
        WHERE plato_id IN ({placeholders})
        ORDER BY plato_id, etiqueta_id
        """,
        tuple(plato_ids),
    )

    agrupado = {plato_id: [] for plato_id in plato_ids}
    for row in rows:
        agrupado[row['plato_id']].append(row['etiqueta_id'])

    return agrupado


def traer_todos_los_platos():
    rows = fetch_all(
        """
        SELECT *
        FROM platos
        ORDER BY plato_id
        """
    )
    platos = [dict(row) for row in rows]
    etiquetas_por_plato = _agrupar_etiquetas_por_plato(
        [plato['plato_id'] for plato in platos]
    )

    for plato in platos:
        plato['etiquetas'] = etiquetas_por_plato.get(plato['plato_id'], [])

    return platos


def eliminar_plato(plato_id: int) -> None:
    existente = fetch_one(
        """
        SELECT plato_id, foto
        FROM platos
        WHERE plato_id = %s
        """,
        (plato_id,),
    )

    if not existente:
        raise ValueError(construir_error_api(
            code='not_found.plato',
            message='Plato no encontrado',
            description=f"No existe un plato con id '{plato_id}'"
        ), 404)

    foto_url = existente['foto']
    if foto_url:
        path = foto_url.split('/platos/')[-1]
        supabase.storage.from_('platos').remove([path])

    execute(
        """
        DELETE FROM plato_etiquetas
        WHERE plato_id = %s
        """,
        (plato_id,),
    )

    execute(
        """
        DELETE FROM platos
        WHERE plato_id = %s
        """,
        (plato_id,),
    )


def actualizar_plato(plato_id: int, data: dict) -> None:
    plato_actual = fetch_one(
        """
        SELECT *
        FROM platos
        WHERE plato_id = %s
        """,
        (plato_id,),
    )

    if not plato_actual:
        raise ValueError(construir_error_api(
            code='not_found.plato',
            message='Plato no encontrado',
            description=f"No existe un plato con id '{plato_id}'"
        ), 404)

    plato_actual = dict(plato_actual)
    campos_actualizar = {}

    if 'nombre' in data:
        duplicado = fetch_one(
            """
            SELECT plato_id
            FROM platos
            WHERE nombre = %s AND plato_id <> %s
            """,
            (data['nombre'], plato_id),
        )
        if duplicado:
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
        _validar_etiquetas_ids(etiquetas)

        execute(
            """
            DELETE FROM plato_etiquetas
            WHERE plato_id = %s
            """,
            (plato_id,),
        )

        if etiquetas:
            _insertar_plato_etiquetas(plato_id, etiquetas)

    if campos_actualizar:
        sets = ', '.join(f'{columna} = %s' for columna in campos_actualizar)
        params = list(campos_actualizar.values()) + [plato_id]
        fila = execute(
            f"""
            UPDATE platos
            SET {sets}
            WHERE plato_id = %s
            """,
            tuple(params),
        )