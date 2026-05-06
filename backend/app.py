from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_connection():
    return pymysql.connect(
        host=os.getenv('TIDB_HOST'),
        port=int(os.getenv('TIDB_PORT', 4000)),
        user=os.getenv('TIDB_USER'),
        password=os.getenv('TIDB_PASSWORD'),
        database=os.getenv('TIDB_DATABASE'),
        ssl={'ca': None},
        cursorclass=pymysql.cursors.DictCursor
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
    
    # Coletar dados
    protocolo = safe_str(dados.get('protocolo'))
    
    # Converter data: "05/05/2026, 17:01:53" -> "2026-05-05 17:01:53"
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
    email = safe_str(dados.get('email'))
    endereco = safe_str(dados.get('endereco'))
    bairro = safe_str(dados.get('bairro'))
    moradores = safe_int_min1(dados.get('moradores'))
    remedio = safe_str(dados.get('remedio'))
    origem = safe_str(dados.get('origem'))
    rg = safe_str(dados.get('rg'))
    sexo = safe_str(dados.get('sexo'))
    peso = safe_float(dados.get('peso'))
    altura = safe_float(dados.get('altura'))
    calcado = safe_str(dados.get('calcado'))
    tamanho_uniforme = safe_str(dados.get('tamanho_uniforme'))
    possui_uniforme = safe_str(dados.get('possui_uniforme'))
    deficiencia = safe_str(dados.get('deficiencia'))
    municipio = safe_str(dados.get('municipio'))
    uf = safe_str(dados.get('uf'))
    escola = safe_str(dados.get('escola'))
    serie = safe_str(dados.get('serie'))
    observacao = safe_str(dados.get('observacao'))
    estrelas = safe_int(dados.get('estrelas'))
    status = 'pendente'
    
    print(f"📥 Recebido: {nome_aluno}, Idade: {idade}, Tamanho: {tamanho_uniforme}, Vínculo: {tipo_vinculo}, Estrelas: {estrelas}")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar duplicata
        cursor.execute("""
            SELECT COUNT(*) as total FROM alunos 
            WHERE rg = %s AND responsavel = %s AND nome_aluno = %s
        """, (rg, responsavel, nome_aluno))
        
        resultado = cursor.fetchone()
        
        if resultado['total'] > 0:
            cursor.close()
            conn.close()
            return jsonify({'erro': 'Aluno já cadastrado'}), 409
        
        # SQL de inserção (com os novos campos)
        sql = """
            INSERT INTO alunos (
                protocolo, data_envio, nome_aluno, data_nasc, idade, turma, 
                categoria, responsavel, tipo_vinculo, sexo_responsavel, telefone, email, 
                endereco, bairro, moradores, remedio, origem, rg, sexo, 
                peso, altura, calcado, tamanho_uniforme, deficiencia, municipio, 
                uf, escola, serie, status, possui_uniforme, observacao, estrelas
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        valores = (
            protocolo, data_envio, nome_aluno, data_nasc, idade, turma, categoria,
            responsavel, tipo_vinculo, sexo_responsavel, telefone, email, 
            endereco, bairro, moradores, remedio, origem, rg, sexo, 
            peso, altura, calcado, tamanho_uniforme, deficiencia, municipio, 
            uf, escola, serie, status, possui_uniforme, observacao, estrelas
        )
        
        cursor.execute(sql, valores)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Aluno salvo! Protocolo: {protocolo}")
        return jsonify({'mensagem': 'Pré-matrícula enviada com sucesso!', 'protocolo': protocolo}), 201
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/elogios', methods=['GET'])
def get_elogios():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome_aluno, observacao, data_envio, estrelas
            FROM alunos 
            WHERE observacao IS NOT NULL AND observacao != ''
            ORDER BY data_envio DESC
            LIMIT 50
        """)
        elogios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(elogios), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'erro': 'Erro ao buscar elogios'}), 500

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos ORDER BY data_envio DESC")
        alunos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(alunos), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'erro': 'Erro ao buscar alunos'}), 500

@app.route('/api/aluno/<protocolo>', methods=['PUT'])
def atualizar_status(protocolo):
    dados = request.json
    novo_status = dados.get('status')
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE alunos SET status = %s WHERE protocolo = %s", (novo_status, protocolo))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'mensagem': f'Status atualizado para {novo_status}'}), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'erro': 'Erro ao atualizar status'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)