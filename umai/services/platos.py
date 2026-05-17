
import logging
from db import supabase

def traer_todos_los_platos():
    platos_resp = (
        supabase.table('platos')
        .select('*')
        .execute()
    )
    return platos_resp.data
