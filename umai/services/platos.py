from db.supabase_client import supabase


def crear_plato(data: dict) -> dict:

    existente = (
        supabase
        .table('platos')
        .select('plato_id')
        .eq('nombre', data['nombre'])
        .execute()
    )

    if existente.data:

        raise ValueError([
            {
                'campo': 'nombre',
                'mensaje': f"Ya existe un plato con el nombre '{data['nombre']}'"
            }
        ])

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

            raise ValueError([
                {
                    'campo': 'etiquetas',
                    'mensaje': f"Las siguientes etiquetas no existen: {etiquetas_invalidas}"
                }
            ])

    foto = data['foto']

    contenido_imagen = foto.read()

    response = (
        supabase
        .table('platos')
        .insert({
            'nombre': data['nombre'],
            'descripcion': data['descripcion'],
            'precio': data['precio'],
            'foto': contenido_imagen
        })
        .execute()
    )

    plato = response.data[0]

    try:

        if etiquetas:

            relaciones = []

            for etiqueta_id in etiquetas:

                relaciones.append({
                    'plato_id': plato['plato_id'],
                    'etiqueta_id': etiqueta_id
                })

            (
                supabase
                .table('plato_etiquetas')
                .insert(relaciones)
                .execute()
            )

    except Exception:

        (
            supabase
            .table('platos')
            .delete()
            .eq('plato_id', plato['plato_id'])
            .execute()
        )

        raise ValueError([
            {
                'campo': 'etiquetas',
                'mensaje': 'Error al asociar las etiquetas al plato'
            }
        ])

    return plato