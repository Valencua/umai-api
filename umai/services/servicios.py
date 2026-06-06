from db.connection import execute, fetch_all, fetch_one
from umai.utils import construir_error_api
from umai.constants import ERROR_CODE_SERVICIO_DUPLICADO

def obtener_servicios() -> list:
    rows = fetch_all(
        """
        SELECT *
        FROM servicios
        """
    )
    if not rows:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_SERVICIO_DUPLICADO,
            message='No se encontraron servicios',
            description='No existen servicios registrados en la base de datos actualmente.'
        ))
        
    return [dict(row) for row in rows]

def crear_servicio(data: dict) -> dict:
    existente = fetch_one(
        """
        SELECT servicio_id
        FROM servicios
        WHERE nombre = %s
        """,
        (data['nombre'],),
    )

    if existente:
        raise ValueError(construir_error_api(
            code='conflict.nombre.duplicate',
            message='Nombre ya registrado',
            description=f"Ya existe un servicio con el nombre '{data['nombre']}'"
        ))

    fila = execute(
        """
        INSERT INTO servicios (nombre, descripcion, icono, estado)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (
            data['nombre'],
            data['descripcion'],
            data['icono'],
            data['estado'],
        ),
        returning=True,
    )

    return dict(fila)


def actualizar_estado_servicio(servicio_id: int, nuevo_estado: bool) -> None:
    existente = fetch_one(
        """
        SELECT servicio_id
        FROM servicios
        WHERE servicio_id = %s
        """,
        (servicio_id,),
    )

    if not existente:
        raise ValueError(construir_error_api(
            code='not_found.servicio',
            message='Servicio no encontrado',
            description=f'No se encontró ningún servicio con el ID {servicio_id}'
        ), 404)

    execute(
        """
        UPDATE servicios
        SET estado = %s
        WHERE servicio_id = %s
        """,
        (nuevo_estado, servicio_id),
    )


def eliminar_servicio(servicio_id: int) -> None:
    existente = fetch_one(
        """
        SELECT servicio_id
        FROM servicios
        WHERE servicio_id = %s
        """,
        (servicio_id,),
    )

    if not existente:
        raise ValueError(construir_error_api(
            code='not_found.servicio',
            message='Servicio no encontrado',
            description=f'No se encontró ningún servicio con el ID {servicio_id}'
        ), 404)

    execute(
        """
        DELETE FROM servicios
        WHERE servicio_id = %s
        """,
        (servicio_id,),
    )