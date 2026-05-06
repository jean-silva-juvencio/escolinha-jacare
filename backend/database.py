import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv('TIDB_HOST'),
        port=int(os.getenv('TIDB_PORT')),
        user=os.getenv('TIDB_USER'),
        password=os.getenv('TIDB_PASSWORD'),
        database=os.getenv('TIDB_DATABASE'),
        cursorclass=pymysql.cursors.DictCursor
    )