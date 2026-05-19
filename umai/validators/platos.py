from umai.constants import MAX_FOTO_BYTES, TIPOS_FOTO_VALIDOS
from umai.utils import construir_error_api, validar_entero, validar_longitud, validar_minimo


def validar_crear_plato(body: dict) -> dict:
    errores = []
    campos_requeridos = ['nombre', 'descripcion', 'precio']

    for campo in campos_requeridos:
        if campo not in body or body[campo] in (None, ''):
            errores.append(construir_error_api(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio y no puede estar vacío"
            )['errors'][0])

    foto = body.get('foto')

    if foto is None or not foto.filename:
        errores.append(construir_error_api(
            code='required.foto',
            message="Campo requerido: 'foto'",
            description="El campo 'foto' es obligatorio"
        )['errors'][0])
    else:
        if foto.content_type not in TIPOS_FOTO_VALIDOS:
            errores.append(construir_error_api(
                code='invalid.foto.format',
                message='Formato de imagen inválido',
                description='La imagen debe ser PNG o JPG'
            )['errors'][0])

        foto.seek(0, 2)
        tamaño = foto.tell()
        foto.seek(0)

        if tamaño > MAX_FOTO_BYTES:
            errores.append(construir_error_api(
                code='invalid.foto.size',
                message='Imagen demasiado grande',
                description='La imagen no puede superar 5MB'
            )['errors'][0])

    precio = None
    if 'precio' in body and body['precio'] not in (None, ''):
        try:
            if isinstance(body['precio'], int):
                precio = body['precio']
            else:
                precio = validar_entero(str(body['precio']), 'precio')
            validar_minimo(precio, 1, 'precio')
        except ValueError as e:
            if isinstance(e.args[0], dict) and 'errors' in e.args[0]:
                errores.extend(e.args[0]['errors'])

    etiquetas = body.get('etiquetas', '')
    etiquetas_lista = []

    if etiquetas:
        try:
            etiquetas_lista = [
                int(etiqueta.strip())
                for etiqueta in etiquetas.split(',')
            ]
        except ValueError:
            errores.append(construir_error_api(
                code='invalid.etiquetas.format',
                message='Formato de etiquetas inválido',
                description='Las etiquetas deben ser IDs numéricos separados por coma'
            )['errors'][0])

    if errores:
        raise ValueError({'errors': errores})

    nombre = body['nombre'].strip()
    descripcion = body['descripcion'].strip()

    try:
        validar_longitud(nombre, 'nombre', min=1, max=100)
        validar_longitud(descripcion, 'descripcion', min=1, max=500)
    except ValueError as e:
        raise ValueError(e.args[0])

    return {
        'nombre': nombre,
        'descripcion': descripcion,
        'precio': precio,
        'foto': foto,
        'etiquetas': etiquetas_lista,
    }