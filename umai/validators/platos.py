from db import supabase
from umai.utils import construir_error_api, validar_longitud
from umai.constants import (
    ERROR_CODE_INVALID_BODY
)

def validar_crear_plato(body: dict) -> dict:
    errores = []

    campos_requeridos = [
        'nombre',
        'descripcion',
        'precio'
    ]
    for campo in campos_requeridos:
        if campo not in body or body[campo] in [None, '']:

            errores.append({
                'campo': campo,
                'mensaje': f"El campo '{campo}' es obligatorio"
            })
    if 'foto' not in body or body['foto'] is None:

        errores.append({
            'campo': 'foto',
            'mensaje': 'La foto es obligatoria'
        })
    else:
        foto = body['foto']

        tipos_validos = [
            'image/png',
            'image/jpeg'
        ]
        if foto.content_type not in tipos_validos:
            errores.append({
                'campo': 'foto',
                'mensaje': 'La imagen debe ser PNG o JPG'
            })

        foto.seek(0, 2)

        tamaño = foto.tell()

        foto.seek(0)

        if tamaño > 5 * 1024 * 1024:

            errores.append({
                'campo': 'foto',
                'mensaje': 'La imagen no puede superar 5MB'
            })

    precio = None
    
    try:

        precio = int(body['precio'])

    except ValueError:

        errores.append({
            'campo': 'precio',
            'mensaje': 'El precio debe ser un numero entero'
        })

    etiquetas = body.get('etiquetas', '')

    etiquetas_lista = []

    if etiquetas:

        try:

            etiquetas_lista = [

                int(etiqueta.strip())

                for etiqueta in etiquetas.split(',')
            ]

        except ValueError:

            errores.append({
                'campo': 'etiquetas',
                'mensaje': 'Las etiquetas deben ser IDs numéricos'
            })

    if errores:

        raise ValueError(errores)

    return {
        'nombre': body['nombre'].strip(),
        'descripcion': body['descripcion'].strip(),
        'precio': precio,
        'foto': body['foto'],
        'etiquetas': etiquetas_lista
    }

def validar_actualizar_plato(body: dict) -> dict:
    errores = []
    data = {}

    if 'nombre' in body and body['nombre']:
        try:
            validar_longitud(body['nombre'], 'nombre', min=3, max=100)
        except ValueError as e:
            errores.extend(e.args[0]['errors'])
        data['nombre'] = body['nombre'].strip()

    if 'descripcion' in body and body['descripcion']:
        try:
            validar_longitud(body['descripcion'], 'descripcion', min=10, max=500)
        except ValueError as e:
            errores.extend(e.args[0]['errors'])
        data['descripcion'] = body['descripcion'].strip()

    if 'precio' in body and body['precio']:
        try:
            data['precio'] = int(body['precio'])
            if data['precio'] <= 0:
                errores.append(construir_error_api(
                    code='invalid.precio.value',
                    message="'precio' inválido",
                    description="El precio debe ser mayor a 0"
                )['errors'][0])
        except (ValueError, TypeError):
            errores.append(construir_error_api(
                code='invalid.precio.format',
                message="'precio' inválido",
                description="El precio debe ser un número entero"
            )['errors'][0])

    if 'foto' in body and body['foto']:
        data['foto'] = body['foto']

    if 'etiquetas' in body:
        data['etiquetas'] = body['etiquetas']

    if not data:
        errores.append(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Sin campos para actualizar',
            description='Debe enviar al menos un campo para actualizar'
        )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    return data