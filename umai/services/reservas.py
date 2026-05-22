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
    HORARIOS_DISPONIBLES,
    FORMATO_FECHA_STR_Z,
    FORMATO_FECHA_STR_zoneinfo,
)

from umai.utils import  a_utc, construir_error_api, formatear_rfc3339, TZ_LOCAL, a_local

logger = logging.getLogger(__name__)


def _obtener_reserva_y_cliente_por_uuid(uuid_codigo: str):
    respuesta = supabase.table('reservas').select('*').eq('uuid_codigo', uuid_codigo).execute()
    if not respuesta.data:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_RESERVA_NO_ENCONTRADA,
            message='Reserva no encontrada',
            description=f'No existe una reserva con el código {uuid_codigo}'
        ))
    reserva = respuesta.data[0]
    cliente = supabase.table('clientes').select('nombre, email, telefono').eq('cliente_id', reserva['cliente_id']).execute()
    datos_cliente = cliente.data[0] if cliente.data else {}
    return reserva, datos_cliente


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


#Tuve un problema de que parece que Supabase te puede cargar distintos formatos de fechas,
#entonces evaluamos cada caso y lo parseamos para que quede como deseamos
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
        }
    }

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
    
def _personas_reservadas_en_turno(str_fecha_utc: str) -> int:
    respuesta = supabase.table('reservas').select('cantidad_personas').eq(
        'fecha', str_fecha_utc
    ).neq(
        'estado', ESTADO_RESERVA_CANCELADO
    ).execute()

    return sum(fila['cantidad_personas'] for fila in respuesta.data)

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

    supabase.table('reservas').insert({
        'cliente_id': cliente_id,
        'fecha': str_fecha_utc,
        'cantidad_personas': data['cantidad_personas'],
        'uuid_codigo': str(codigo),
        'qr_url': qr_url,
        'estado': ESTADO_RESERVA_PENDIENTE,
    }).execute()
    print(str_fecha_utc)


def confirmar_reserva_por_codigo(uuid_codigo: str) -> dict:
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

    actualizado = supabase.table('reservas').update({
        'estado': ESTADO_RESERVA_CANCELADO,
    }).eq('uuid_codigo', uuid_codigo).execute()

    return _serializar_reserva(actualizado.data[0], datos_cliente)

def obtener_reservas(limit=None, offset=None, orden='desc', uuid_codigo=None) -> list:
    query = supabase.table('reservas').select('*, clientes(nombre, email, telefono)')

    if uuid_codigo:
        query = query.eq('uuid_codigo', uuid_codigo)

    query = query.order('reserva_id', desc=(orden == 'desc'))

    if limit is not None:
        query = query.limit(limit)

    if offset is not None:
        query = query.offset(offset)

    respuesta = query.execute()

    resultado = []
    for r in respuesta.data:
        datos_cliente = r.pop('clientes', {}) or {}
        resultado.append(_serializar_reserva(r, datos_cliente))

    return resultado

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

