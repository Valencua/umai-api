import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('Falta DATABASE_URL en .env')


def get_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except psycopg2.OperationalError as e:
        logger.error('Error al conectar con la base de datos')
        raise RuntimeError(f'No se pudo conectar a la base de datos: {e}')


def fetch_all(sql: str, params=None) -> list:
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(sql, params or ())
            return cur.fetchall()
        finally:
            cur.close()
    finally:
        conn.close()


def fetch_one(sql: str, params=None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params=None, returning: bool = False):
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(sql, params or ())
            row = cur.fetchone() if returning else None
            conn.commit()
            return row
        finally:
            cur.close()
    finally:
        conn.close()