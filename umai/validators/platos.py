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