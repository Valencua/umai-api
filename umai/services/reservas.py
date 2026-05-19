import logging
import uuid
from datetime import datetime, timezone

from db import supabase
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
    FORMATO_FECHA, 
    FORMATO_HORARIO,
    HORARIOS_DISPONIBLES
)

from umai.utils import a_local, a_utc, construir_error_api, formatear_rfc3339, TZ_LOCAL

logger = logging.getLogger(__name__)

def _obtener_o_crear_cliente(nombre: str, email: str, telefono: str) -> int:
    respuesta = supabase.table('clientes').select('cliente_id').eq('email', email).execute()

    if respuesta.data:
        cliente_id = respuesta.data[0]['cliente_id']
        supabase.table('clientes').update({
            'nombre': nombre,
            'telefono': telefono,
        }).eq('cliente_id', cliente_id).execute()
        return cliente_id

    insertado = supabase.table('clientes').insert({
        'nombre': nombre,
        'email': email,
        'telefono': telefono,
    }).execute()

    return insertado.data[0]['cliente_id']

def _parsear_fecha_utc(fecha_raw) -> datetime:
    if isinstance(fecha_raw, str):
        fecha = datetime.fromisoformat(fecha_raw.replace('Z', '+00:00'))
    else:
        fecha = fecha_raw

    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)

    return fecha

def _tiene_reserva_activa(email: str) -> bool:
    respuesta_cliente = supabase.table('clientes').select('cliente_id').eq('email', email).execute()

    if not respuesta_cliente.data:
        return False

    cliente_id = respuesta_cliente.data[0]['cliente_id']
    respuesta = supabase.table('reservas').select('fecha, estado').eq(
        'cliente_id', cliente_id
    ).neq(
        'estado', ESTADO_RESERVA_CANCELADO
    ).execute()

    ahora = datetime.now(timezone.utc)

    for reserva in respuesta.data:
        if _parsear_fecha_utc(reserva['fecha']) >= ahora:
            return True

    return False

def _personas_reservadas_en_turno(fecha_hora_utc_iso: str) -> int:
    respuesta = supabase.table('reservas').select('cantidad_personas').eq(
        'fecha', fecha_hora_utc_iso
    ).neq(
        'estado', ESTADO_RESERVA_CANCELADO
    ).execute()

    return sum(fila['cantidad_personas'] for fila in respuesta.data)

def _obtener_reserva_y_cliente_por_uuid(uuid_codigo: str) -> tuple[dict, dict]:
    respuesta = supabase.table('reservas').select(
        'reserva_id, cliente_id, fecha, cantidad_personas, uuid_codigo, qr_url, estado, '
        'clientes(nombre, email, telefono)'
    ).eq('uuid_codigo', uuid_codigo).execute()

    if not respuesta.data:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_NO_ENCONTRADA,
            message='Reserva no encontrada',
            description=f"No existe una reserva con el codigo '{uuid_codigo}'"
        ))

    fila = respuesta.data[0]
    cliente = fila.pop('clientes') or {}
    datos_cliente = {
        'nombre': cliente.get('nombre', ''),
        'email': cliente.get('email', ''),
        'telefono': cliente.get('telefono', ''),
    }
    return fila, datos_cliente


def _serializar_reserva(reserva: dict, datos_cliente: dict) -> dict:
    fecha_utc = _parsear_fecha_utc(reserva['fecha'])
    fecha_local = a_local(fecha_utc)

    return {
        'reserva_id': reserva['reserva_id'],
        'nombre': datos_cliente['nombre'],
        'email': datos_cliente['email'],
        'telefono': datos_cliente['telefono'],
        'fecha': formatear_rfc3339(fecha_utc),
        'horario': fecha_local.strftime('%H:%M'),
        'cantidad_personas': reserva['cantidad_personas'],
        'uuid_codigo': reserva['uuid_codigo'],
        'qr_url': reserva['qr_url'],
        'estado': reserva['estado'],
    }

def crear_reserva(data: dict) -> dict:
    fecha_hora_utc_iso = data['fecha_hora_utc'].isoformat().replace('+00:00', 'Z') #EJ formato ISO '2026-05-20T23:00:00+00:00' → reemplaza +00:00 por Z 2026-05-20T23:00:00Z

    personas_en_turno = _personas_reservadas_en_turno(fecha_hora_utc_iso)
    if personas_en_turno + data['cantidad_personas'] > CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO:
        logger.warning(
            'Turno lleno para %s: %s personas ya reservadas',
            fecha_hora_utc_iso,
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

    insertado = supabase.table('reservas').insert({
        'cliente_id': cliente_id,
        'fecha': fecha_hora_utc_iso,
        'cantidad_personas': data['cantidad_personas'],
        'uuid_codigo': str(codigo),
        'qr_url': qr_url,
        'estado': ESTADO_RESERVA_PENDIENTE,
    }).execute()

    return _serializar_reserva(insertado.data[0], data)

def confirmar_asistencia_por_codigo(uuid_codigo: str) -> dict:
    reserva, datos_cliente = _obtener_reserva_y_cliente_por_uuid(uuid_codigo)

    if reserva['estado'] == ESTADO_RESERVA_CANCELADO:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_CANCELADA,
            message='No se puede confirmar asistencia',
            description='La reserva esta cancelada y no puede marcarse como asistida'
        ))

    if reserva['estado'] == ESTADO_RESERVA_CONFIRMADO:
        return _serializar_reserva(reserva, datos_cliente)

    actualizado = supabase.table('reservas').update({
        'estado': ESTADO_RESERVA_CONFIRMADO,
    }).eq('uuid_codigo', uuid_codigo).execute()

    return _serializar_reserva(actualizado.data[0], datos_cliente)

def obtener_reservas():
    reservas = (
        supabase.table('reservas')
        .select('*')
        .order('reserva_id', desc=True)
        .execute()
    )

    for reserva in reservas.data:
        fecha = reserva.get('fecha')
        
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha.replace('Z', '+00:00'))

        if isinstance(fecha, datetime):
            reserva['fecha'] = a_local(fecha)

    return reservas.data

def get_top3_reservas():
    reservas_recientes = (
        supabase.table('reservas')
        .select('*')
        .order('reserva_id', desc=True)
        .limit(3)
        .execute()
    )

    for reserva in reservas_recientes.data:
        fecha = reserva.get('fecha')
        
        if fecha:
            if isinstance(fecha, str):
                fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
            else:
                fecha_dt = fecha
            fecha_local = a_local(fecha_dt)
            reserva['fecha'] = formatear_rfc3339(fecha_local)
            reserva['fecha'] = fecha_local.strftime(f"{FORMATO_FECHA} {FORMATO_HORARIO}")

    return reservas_recientes.data

def obtener_reservas_codigo(uuid_codigo):

    response = supabase.table('reservas').select('*,clientes(*)').eq('uuid_codigo', uuid_codigo).execute()

    if not response.data:
        return None

    return response.data[0]

def obtener_disponibilidad(fecha: str):
    try:
        fecha_obj = datetime.strptime(
            fecha, '%Y-%m-%d'
        ).date()
        
    except ValueError:

            raise ValueError(construir_error_api(
                code='invalid.fecha',
                message='Fecha inválida',
                description='La fecha debe tener formato YYYY-MM-DD'
            ))

    hoy = datetime.now(timezone.utc).date()

    if fecha_obj < hoy:

        raise ValueError(construir_error_api(
            code='invalid.fecha.pasada',
            message='Fecha inválida',
            description='No se puede consultar disponibilidad para fechas pasadas'
        ))
    disponibilidad = []

    for horario in HORARIOS_DISPONIBLES:

        fecha_local = datetime.strptime(
        f'{fecha} {horario}',
        '%Y-%m-%d %H:%M'
        ).replace(tzinfo=TZ_LOCAL)

        fecha_utc = a_utc(fecha_local)
        
        fecha_hora = fecha_utc.isoformat().replace('+00:00','Z')
        
        response = (
            supabase
            .table('reservas')
            .select('cantidad_personas')
            .eq('fecha', fecha_hora)
            .neq('estado', ESTADO_RESERVA_CANCELADO)
            .execute()
        )
         
        personas_reservadas = sum(
            reserva['cantidad_personas']
            for reserva in response.data
        )
        
        lugares_disponibles = (
            CAPACIDAD_MAXIMA_PERSONAS_POR_TURNO - personas_reservadas
        )
        
        disponibilidad.append({
            'horario': horario,
            'lugares_disponibles': lugares_disponibles,
            'disponible': lugares_disponibles > 0
        })
    return disponibilidad

def cancelar_reserva_por_codigo(uuid_codigo: str) -> dict:
    reserva, datos_cliente = _obtener_reserva_y_cliente_por_uuid(uuid_codigo)

    if reserva['estado'] == ESTADO_RESERVA_CANCELADO:
        return _serializar_reserva(reserva, datos_cliente)

    if reserva['estado'] == ESTADO_RESERVA_CONFIRMADO:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_YA_CONFIRMADA,
            message='No se puede cancelar la reserva',
            description='La reserva ya fue confirmada (asistencia registrada) y no puede cancelarse'
        ))

    actualizado = supabase.table('reservas').update({
        'estado': ESTADO_RESERVA_CANCELADO,
    }).eq('uuid_codigo', uuid_codigo).execute()

    return _serializar_reserva(actualizado.data[0], datos_cliente)

