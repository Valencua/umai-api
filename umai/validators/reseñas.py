from umai.utils import validar_entero

def validar_id_reseña(id_reseña: str) -> int:
    return validar_entero(id_reseña, 'id')