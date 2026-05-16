from flask import Blueprint, jsonify, request
from umai.services.reseñas import crear_reseña
from umai.utils import construir_error_api

reseñas_bp = Blueprint('reseñas', __name__)

@reseñas_bp.route('/', methods=['POST'])
def post_reseña():
    body = request.get_json()

    if not body:
        return jsonify(construir_error_api(
            code='MISSING_FIELDS',
            message='Body vacio',
            description='El body no puede estar vacio'
        )), 400

    cliente_id = body.get('cliente_id')
    descripcion = body.get('descripcion')
    rating = body.get('rating')    

    if not cliente_id or not descripcion or rating is None:
        return jsonify(construir_error_api(
            code='MISSING_FIELDS',
            message='Faltan campos requeridos',
            description='cliente_id, descripcion y rating son obligatorios'
        )),400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify(construir_error_api(
            code='INVALID_FIELDS',
            message='Rating invalido',
            description='Rating debe ser un numero entre el 1 y 5'
        )), 400   

    reseña = crear_reseña(cliente_id, descripcion, rating)

    if reseña is None:
        return jsonify(construir_error_api(
            code='SERVER_ERROR',
            message='No se puede crear la reseña',
            description='Ocurrio un error inesperado'
        )), 500

    return jsonify({'data': reseña, 'status':'success'}), 201         