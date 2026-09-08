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
    data_inscricao = safe_str(dados.get('data_inscricao'))
    # CORRIGIDO: usa None se estiver vazio
    data_entrega_uniforme = dados.get('data_entrega_uniforme') or None
    status = 'pendente'

    print(f"📥 Recebido: {nome_aluno}, Idade: {idade}, Tamanho: {tamanho_uniforme}")

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

        # SQL de inserção com as novas colunas
        sql = """
            INSERT INTO alunos (
                protocolo, data_envio, nome_aluno, data_nasc, idade, turma, 
                categoria, responsavel, tipo_vinculo, sexo_responsavel, telefone, email, 
                endereco, bairro, moradores, remedio, origem, rg, sexo, 
                peso, altura, calcado, tamanho_uniforme, deficiencia, municipio, 
                uf, escola, serie, status, possui_uniforme, observacao, estrelas,
                data_inscricao, data_entrega_uniforme
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        valores = (
            protocolo, data_envio, nome_aluno, data_nasc, idade, turma, categoria,
            responsavel, tipo_vinculo, sexo_responsavel, telefone, email, 
            endereco, bairro, moradores, remedio, origem, rg, sexo, 
            peso, altura, calcado, tamanho_uniforme, deficiencia, municipio, 
            uf, escola, serie, status, possui_uniforme, observacao, estrelas,
            data_inscricao, data_entrega_uniforme
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

@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos ORDER BY id DESC")
        alunos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(alunos), 200
    except Exception as e:
        print(f"❌ Erro ao buscar alunos: {e}")
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
        print(f"❌ Erro ao atualizar status: {e}")
        return jsonify({'erro': 'Erro ao atualizar status'}), 500

# ==================== ROTA DE EDIÇÃO ====================
@app.route('/api/aluno/editar/<protocolo>', methods=['PUT'])
def atualizar_aluno(protocolo):
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

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE alunos SET
                nome_aluno = %s,
                data_nasc = %s,
                idade = %s,
                turma = %s,
                categoria = %s,
                responsavel = %s,
                tipo_vinculo = %s,
                sexo_responsavel = %s,
                telefone = %s,
                email = %s,
                endereco = %s,
                bairro = %s,
                moradores = %s,
                remedio = %s,
                origem = %s,
                rg = %s,
                sexo = %s,
                peso = %s,
                altura = %s,
                calcado = %s,
                tamanho_uniforme = %s,
                possui_uniforme = %s,
                deficiencia = %s,
                municipio = %s,
                uf = %s,
                escola = %s,
                serie = %s,
                observacao = %s,
                estrelas = %s,
                data_entrega_uniforme = %s
            WHERE protocolo = %s
        """

        # CORRIGIDO: data_entrega_uniforme usa None se estiver vazio
        valores = (
            safe_str(dados.get('nome_aluno')),
            safe_str(dados.get('data_nasc')),
            safe_int(dados.get('idade')),
            safe_str(dados.get('turma')),
            safe_str(dados.get('categoria')),
            safe_str(dados.get('responsavel')),
            safe_str(dados.get('tipo_vinculo')),
            safe_str(dados.get('sexo_responsavel')),
            safe_str(dados.get('telefone')),
            safe_str(dados.get('email')),
            safe_str(dados.get('endereco')),
            safe_str(dados.get('bairro')),
            safe_int_min1(dados.get('moradores')),
            safe_str(dados.get('remedio')),
            safe_str(dados.get('origem')),
            safe_str(dados.get('rg')),
            safe_str(dados.get('sexo')),
            safe_float(dados.get('peso')),
            safe_float(dados.get('altura')),
            safe_str(dados.get('calcado')),
            safe_str(dados.get('tamanho_uniforme')),
            safe_str(dados.get('possui_uniforme')),
            safe_str(dados.get('deficiencia')),
            safe_str(dados.get('municipio')),
            safe_str(dados.get('uf')),
            safe_str(dados.get('escola')),
            safe_str(dados.get('serie')),
            safe_str(dados.get('observacao')),
            safe_int(dados.get('estrelas')),
            dados.get('data_entrega_uniforme') or None,  # <--- CORRIGIDO
            protocolo
        )

        cursor.execute(sql, valores)
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'erro': 'Aluno não encontrado'}), 404

        cursor.close()
        conn.close()

        print(f"✅ Aluno atualizado! Protocolo: {protocolo}")
        return jsonify({'mensagem': 'Aluno atualizado com sucesso!'}), 200

    except Exception as e:
        print(f"❌ Erro ao atualizar aluno: {e}")
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
        print(f"❌ Erro ao buscar elogios: {e}")
        return jsonify({'erro': 'Erro ao buscar elogios'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
