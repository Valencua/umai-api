import logging
import uuid
from datetime import datetime, timezone

from db.connection import execute, fetch_all, fetch_one
from umai.constants import (
    CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO,
    ERROR_CODE_RESERVA_ACTIVA,
    ERROR_CODE_TURNO_LLENO,
    ESTADO_RESERVA_CANCELADO,
    ESTADO_RESERVA_PENDIENTE,
    ERROR_CODE_RESERVA_NO_ENCONTRADA,
    ERROR_CODE_RESERVA_YA_CONFIRMADA,
    ESTADO_RESERVA_CONFIRMADO,
    ERROR_CODE_RESERVA_CANCELADA,
    HORARIOS_DISPONIBLES,
    FORMATO_FECHA_STR_Z,
    FORMATO_FECHA,
    ERROR_CODE_RESERVA_TURNO_PASADO,
)
from umai.utils import a_utc, construir_error_api, formatear_rfc3339, TZ_LOCAL

logger = logging.getLogger(__name__)


def _obtener_reserva_y_cliente_por_uuid(uuid_codigo: str):
    row = fetch_one(
        """
        SELECT r.*,
               c.nombre AS cliente_nombre,
               c.email AS cliente_email,
               c.telefono AS cliente_telefono
        FROM reservas r
        JOIN clientes c ON c.cliente_id = r.cliente_id
        WHERE r.uuid_codigo = %s
        """,
        (uuid_codigo,),
    )

    if not row:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_NO_ENCONTRADA,
            message='Reserva no encontrada',
            description=f'No existe una reserva con el cÃ³digo {uuid_codigo}'
        ))

    reserva = dict(row)
    datos_cliente = {
        'nombre': reserva.pop('cliente_nombre', None),
        'email': reserva.pop('cliente_email', None),
        'telefono': reserva.pop('cliente_telefono', None),
    }
    return reserva, datos_cliente


def _obtener_o_crear_cliente(nombre: str, email: str, telefono: str) -> int:
    existente = fetch_one(
        """
        SELECT cliente_id
        FROM clientes
        WHERE email = %s
        """,
        (email,),
    )

    if existente:
        cliente_id = existente['cliente_id']
        execute(
            """
            UPDATE clientes
            SET nombre = %s, telefono = %s
            WHERE cliente_id = %s
            """,
            (nombre, telefono, cliente_id),
        )
        return cliente_id

    fila = execute(
        """
        INSERT INTO clientes (nombre, email, telefono)
        VALUES (%s, %s, %s)
        RETURNING cliente_id
        """,
        (nombre, email, telefono),
        returning=True,
    )
    return fila['cliente_id']


def _parsear_fecha_utc(fecha_raw) -> datetime:
    if isinstance(fecha_raw, str):
        s = fecha_raw.strip().replace(' ', 'T')
        if '+00:00' in s:
            s = s.replace('+00:00', 'Z')
        elif s.endswith('+00'):
            s = s.replace('+00', 'Z')

        if s.endswith('Z') and '.' not in s.split('T')[-1]:
            s = s.replace('Z', '.000000Z')
        fecha = datetime.strptime(s, FORMATO_FECHA_STR_Z)
    else:
        fecha = fecha_raw
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return fecha


def _serializar_reserva(reserva: dict, datos_cliente: dict) -> dict:
    fecha_raw = reserva.get('fecha')
    fecha_local = None
    if fecha_raw:
        fecha_dt = _parsear_fecha_utc(fecha_raw)
        fecha_local = formatear_rfc3339(fecha_dt)

    return {
        'reserva_id': reserva.get('reserva_id'),
        'uuid_codigo': reserva.get('uuid_codigo'),
        'estado': reserva.get('estado'),
        'fecha': fecha_local,
        'cantidad_personas': reserva.get('cantidad_personas'),
        'qr_url': reserva.get('qr_url'),
        'cliente': {
            'nombre': datos_cliente.get('nombre'),
            'email': datos_cliente.get('email'),
            'telefono': datos_cliente.get('telefono'),
        },
    }


def _tiene_reserva_activa(email: str) -> bool:
    cliente = fetch_one(
        """
        SELECT cliente_id
        FROM clientes
        WHERE email = %s
        """,
        (email,),
    )

    if not cliente:
        return False

    reservas = fetch_all(
        """
        SELECT fecha, estado
        FROM reservas
        WHERE cliente_id = %s AND estado <> %s
        """,
        (cliente['cliente_id'], ESTADO_RESERVA_CANCELADO),
    )

    ahora = datetime.now(timezone.utc)

    for reserva in reservas:
        if _parsear_fecha_utc(reserva['fecha']) >= ahora:
            return True

    return False


def _personas_reservadas_en_turno(str_fecha_utc: str) -> int:
    filas = fetch_all(
        """
        SELECT cantidad_personas
        FROM reservas
        WHERE fecha = %s AND estado <> %s
        """,
        (str_fecha_utc, ESTADO_RESERVA_CANCELADO),
    )
    return sum(fila['cantidad_personas'] for fila in filas)


def crear_reserva(data: dict) -> dict:
    str_fecha_utc = data['fecha_hora_utc'].strftime(FORMATO_FECHA_STR_Z)

    personas_en_turno = _personas_reservadas_en_turno(str_fecha_utc)
    if personas_en_turno + data['cantidad_personas'] > CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO:
        logger.warning(
            'Turno lleno para %s: %s personas ya reservadas',
            str_fecha_utc,
            personas_en_turno,
        )
        raise ValueError(construir_error_api(
            code=ERROR_CODE_TURNO_LLENO,
            message='Turno sin disponibilidad',
            description=(
                f'El turno ya alcanzo el maximo de {CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO} '
                'personas reservadas'
            )
        ))

    if _tiene_reserva_activa(data['email']):
        logger.warning('Cliente con reserva activa intento reservar de nuevo: %s', data['email'])
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_ACTIVA,
            message='Ya tenes una reserva activa',
            description=(
                'Solo podes tener una reserva a la vez. '
                'Cancela la actual o espera a que pase el turno para reservar de nuevo'
            )
        ))

    cliente_id = _obtener_o_crear_cliente(
        data['nombre'],
        data['email'],
        data['telefono'],
    )

    codigo = uuid.uuid4()
    qr_url = f'https://umai.example/qr/{codigo}'

    execute(
        """
        INSERT INTO reservas (
            cliente_id, fecha, cantidad_personas,
            uuid_codigo, qr_url, estado
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            cliente_id,
            str_fecha_utc,
            data['cantidad_personas'],
            str(codigo),
            qr_url,
            ESTADO_RESERVA_PENDIENTE,
        ),
    )


def confirmar_reserva_por_codigo(uuid_codigo: str) -> dict:
    reserva, datos_cliente = _obtener_reserva_y_cliente_por_uuid(uuid_codigo)
    if reserva['estado'] == ESTADO_RESERVA_CANCELADO:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_CANCELADA,
            message='No se puede confirmar asistencia',
            description='La reserva esta cancelada y no puede marcarse como asistida'
        ))
    if _parsear_fecha_utc(reserva['fecha']) < datetime.now(timezone.utc):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_TURNO_PASADO,
            message='No se puede confirmar la reserva',
            description='El turno de la reserva ya finalizo',
        ))
    if reserva['estado'] == ESTADO_RESERVA_CONFIRMADO:
        return _serializar_reserva(reserva, datos_cliente)
    actualizado = execute(
        """
        UPDATE reservas
        SET estado = %s
        WHERE uuid_codigo = %s
        RETURNING *
        """,
        (ESTADO_RESERVA_CONFIRMADO, uuid_codigo),
        returning=True,
    )
    return _serializar_reserva(dict(actualizado), datos_cliente)
def cancelar_reserva_por_codigo(uuid_codigo: str) -> dict:
    reserva, datos_cliente = _obtener_reserva_y_cliente_por_uuid(uuid_codigo)
    if reserva['estado'] == ESTADO_RESERVA_CANCELADO:
        return _serializar_reserva(reserva, datos_cliente)
    if reserva['estado'] == ESTADO_RESERVA_CONFIRMADO:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_YA_CONFIRMADA,
            message='No se puede cancelar la reserva',
            description='La reserva ya fue confirmada y no puede cancelarse'
        ))
    actualizado = execute(
        """
        UPDATE reservas
        SET estado = %s
        WHERE uuid_codigo = %s
        RETURNING *
        """,
        (ESTADO_RESERVA_CANCELADO, uuid_codigo),
        returning=True,
    )
    return _serializar_reserva(dict(actualizado), datos_cliente)


def obtener_reservas(limit=None, offset=None, orden='desc', uuid_codigo=None) -> list:
    sql = """
        SELECT r.*,
               c.nombre AS cliente_nombre,
               c.email AS cliente_email,
               c.telefono AS cliente_telefono
        FROM reservas r
        JOIN clientes c ON c.cliente_id = r.cliente_id
    """
    params = []

    if uuid_codigo:
        sql += ' WHERE r.uuid_codigo = %s'
        params.append(uuid_codigo)

    sql += f" ORDER BY r.reserva_id {'DESC' if orden == 'desc' else 'ASC'}"

    if limit is not None:
        sql += ' LIMIT %s'
        params.append(limit)

    if offset is not None:
        sql += ' OFFSET %s'
        params.append(offset)

    rows = fetch_all(sql, tuple(params))

    resultado = []
    for row in rows:
        fila = dict(row)
        datos_cliente = {
            'nombre': fila.pop('cliente_nombre', None),
            'email': fila.pop('cliente_email', None),
            'telefono': fila.pop('cliente_telefono', None),
        }
        resultado.append(_serializar_reserva(fila, datos_cliente))

    return resultado


def obtener_disponibilidad(fecha_obj) -> list[dict]:
    fecha_str = fecha_obj.strftime(FORMATO_FECHA)
    disponibilidad = []

    for horario in HORARIOS_DISPONIBLES:
        fecha_local = datetime.strptime(f'{fecha_str} {horario}','%Y-%m-%d %H:%M',).replace(tzinfo=TZ_LOCAL)

        fecha_utc = a_utc(fecha_local)
        str_fecha_utc = fecha_utc.strftime(FORMATO_FECHA_STR_Z)

        filas = fetch_all(
            """
            SELECT cantidad_personas
            FROM reservas
            WHERE fecha = %s AND estado <> %s
            """,
            (str_fecha_utc, ESTADO_RESERVA_CANCELADO),
        )

        personas_reservadas = sum(fila['cantidad_personas'] for fila in filas)

        lugares_disponibles = (
            CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO - personas_reservadas
        )

        disponibilidad.append({
            'horario': horario,
            'lugares_disponibles': lugares_disponibles,
            'disponible': lugares_disponibles > 0,
        })

    return disponibilidad