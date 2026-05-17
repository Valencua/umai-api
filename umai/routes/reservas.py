from flask import Blueprint, jsonify, request


reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/', methods=['POST'])
def post_reserva():
    """
    Acá tenemos que recibir 201 si es creada
    400 BAD REQUEST si faltan campos, fecha pasada, horario no disponible
    409 si turno lleno
    Primero validar los datos (aca todo con validators)
    Despues validar fecha
    Luego validar horario
    Si todo corre bien, crear reserva en el service
    """
    return jsonify(), 201

