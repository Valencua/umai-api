from db import supabase

def eliminar_reseña(reseña_id: int):
    try:
        respuesta = (supabase.table('reseñas').delete().eq('reseña_id', reseña_id).execute())

        if not respuesta.data:
            return False
        
        return True
    
    except Exception as e:
        print(f"Error al eliminar reseña: {str(e)}")
        return None
