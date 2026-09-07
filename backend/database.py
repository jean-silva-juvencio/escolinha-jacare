import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('NEON_HOST'),
        port=int(os.getenv('NEON_PORT')),
        user=os.getenv('NEON_USER'),
        password=os.getenv('NEON_PASSWORD'),
        database=os.getenv('NEON_DATABASE'),
        sslmode='require',
        cursor_factory=psycopg2.extras.RealDictCursor
    )
