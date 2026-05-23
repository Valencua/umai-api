from datetime import datetime, timezone

from db.connection import execute, fetch_all, fetch_one
from umai.constants import ESTADO_RESERVA_CONFIRMADO
from umai.utils import construir_error_api, formatear_rfc3339


def _serializar_reseña(fila: dict) -> dict:
    out = dict(fila)
    if out.get('creado_en') is not None:
        out['creado_en'] = formatear_rfc3339(out['creado_en'])
    return out


def _fila_listado_reseña(row: dict) -> dict:
    return {
        'reseña_id': row['reseña_id'],
        'descripcion': row['descripcion'],
        'rating': row['rating'],
        'creado_en': formatear_rfc3339(row['creado_en']),
        'clientes': {'nombre': row['nombre']},
    }


def listar_reseñas(estado: bool) -> list:
    rows = fetch_all(
        """
        SELECT r.reseña_id, r.descripcion, r.rating, r.creado_en, c.nombre
        FROM reseñas r
        JOIN clientes c ON c.cliente_id = r.cliente_id
        WHERE r.estado = %s
        ORDER BY r.creado_en DESC
        """,
        (estado,),
    )
    return [_fila_listado_reseña(row) for row in rows]


def eliminar_reseña(resena_id: int) -> None:
    existente = fetch_one(
        """
        SELECT reseña_id
        FROM reseñas
        WHERE reseña_id = %s
        """,
        (resena_id,),
    )

    if not existente:
        raise ValueError(construir_error_api(
            code='not_found.resena',
            message='Reseña no encontrada',
            description=f"No existe una reseña con id '{resena_id}'"
        ), 404)

    execute(
        """
        DELETE FROM reseñas
        WHERE reseña_id = %s
        """,
        (resena_id,),
    )


def crear_reseña(data: dict) -> dict:
    cliente = fetch_one(
        """
        SELECT cliente_id
        FROM clientes
        WHERE email = %s
        """,
        (data['email'],),
    )

    if not cliente:
        raise ValueError(construir_error_api(
            code='not_found.cliente',
            message='Cliente no encontrado',
            description=f"No existe un cliente con el email '{data['email']}'"
        ), 404)

    cliente_id = cliente['cliente_id']

    reserva = fetch_one(
        """
        SELECT reserva_id
        FROM reservas
        WHERE cliente_id = %s AND estado = %s
        LIMIT 1
        """,
        (cliente_id, ESTADO_RESERVA_CONFIRMADO),
    )

    if not reserva:
        raise ValueError(construir_error_api(
            code='forbidden.resena.sin_reserva',
            message='Sin reserva confirmada',
            description='Necesitás al menos una visita confirmada para dejar una reseña'
        ), 403)

    ya_reseño = fetch_one(
        """
        SELECT reseña_id
        FROM reseñas
        WHERE cliente_id = %s
        LIMIT 1
        """,
        (cliente_id,),
    )

    if ya_reseño:
        raise ValueError(construir_error_api(
            code='conflict.resena.duplicada',
            message='Ya existe una reseña',
            description='Ya dejaste una reseña anteriormente'
        ), 409)

    creado_en = datetime.now(timezone.utc)

    fila = execute(
        """
        INSERT INTO reseñas (cliente_id, rating, descripcion, estado, creado_en)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            cliente_id,
            data['rating'],
            data['descripcion'],
            False,
            creado_en,
        ),
        returning=True,
    )

    return _serializar_reseña(fila)


def actualizar_estado_reseña(reseña_id: int, nuevo_estado: bool) -> dict:
    existente = fetch_one(
        """
        SELECT reseña_id
        FROM reseñas
        WHERE reseña_id = %s
        """,
        (reseña_id,),
    )

    if not existente:
        raise ValueError(construir_error_api(
            code='not_found.reseña',
            message='reseña no encontrada',
            description=f'No se encontró ningúna reseña con el ID {reseña_id}'
        ), 404)

    fila = execute(
        """
        UPDATE reseñas
        SET estado = %s
        WHERE reseña_id = %s
        RETURNING *
        """,
        (nuevo_estado, reseña_id),
        returning=True,
    )

    return _serializar_reseña(fila)