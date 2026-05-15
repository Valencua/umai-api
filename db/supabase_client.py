import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        'Faltan credenciales en el entorno.'
        'Revisa archivo .env (debe seguir el modelo .env.example)'
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)