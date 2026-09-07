from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_connection():
    return psycopg2.connect(
        host=os.getenv('NEON_HOST'),
        port=int(os.getenv('NEON_PORT', 5432)),
        user=os.getenv('NEON_USER'),
        password=os.getenv('NEON_PASSWORD'),
        database=os.getenv('NEON_DATABASE'),
        sslmode='require',
        cursor_factory=psycopg2.extras.RealDictCursor
    )

@app.route('/')
def home():
    return jsonify({'mensagem': 'API da Escolinha do Jacaré funcionando!'})

@app.route('/api/prematricula', methods=['POST'])
def prematricula():
    dados = request.json

    def safe_str(valor):
        return '' if valor is None else str(valor)

    def safe_int(valor):
        if valor is None or valor == '':
            return 0
        try:
            return int(float(valor))
        except:
            return 0

    def safe_int_min1(valor):
        if valor is None or valor == '':
            return 1
        try:
            return int(float(valor))
        except:
            return 1

    def safe_float(valor):
        if valor is None or valor == '':
            return 0
        try:
            return float(valor)
        except:
            return 0

    protocolo = safe_str(dados.get('protocolo'))

    data_envio_raw = safe_str(dados.get('dataEnvio'))
    try:
        dt = datetime.strptime(data_envio_raw, "%d/%m/%Y, %H:%M:%S")
        data_envio = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        data_envio = data_envio_raw.replace('/', '-').replace(',', '')

    nome_aluno = safe_str(dados.get('nomeAluno'))
    data_nasc = safe_str(dados.get('dataNasc'))
    idade = safe_int(dados.get('idade'))
    turma = safe_str(dados.get('turma'))
    categoria = safe_str(dados.get('categoria'))
    responsavel = safe_str(dados.get('responsavel'))
    tipo_vinculo = safe_str(dados.get('tipo_vinculo'))
    sexo_responsavel = safe_str(dados.get('sexo_responsavel'))
    telefone = safe_str(dados.get('telefone'))
    email =
