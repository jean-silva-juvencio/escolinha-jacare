from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime
import cloudinary
import cloudinary.uploader

load_dotenv()

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURAÇÃO CLOUDINARY ====================
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'PBMaz3jx'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '545953851437675'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'HNzome7Mzq0Ks1ZrhjeHcG8DvNQ'),
    secure=True
)

# Status do sistema (persistido em memória)
sistema_status = {
    'online': True,
    'ultima_atualizacao': datetime.now().isoformat()
}

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

# ==================== LOGIN ====================
@app.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    email = dados.get('email', '').strip()
    senha = dados.get('senha', '').strip()
    
    if not email or not senha:
        return jsonify({'erro': 'Digite e-mail e senha!'}), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Busca o usuário pelo email
        cursor.execute("""
            SELECT id, nome, email, senha, cargo, ativo 
            FROM usuarios 
            WHERE email = %s
        """, (email,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({'erro': 'E-mail ou senha incorretos'}), 401
        
        if not usuario['ativo']:
            cursor.close()
            conn.close()
            return jsonify({'erro': 'Usuário desativado. Fale com o administrador.'}), 401
        
        # Verifica a senha (comparação direta)
        if usuario['senha'] != senha:
            cursor.close()
            conn.close()
            return jsonify({'erro': 'E-mail ou senha incorretos'}), 401
        
        # Atualiza último acesso
        cursor.execute("UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = %s", (usuario['id'],))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Login: {usuario['nome']} ({usuario['email']})")
        
        return jsonify({
            'mensagem': 'Login realizado com sucesso!',
            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'cargo': usuario['cargo']
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': 'Erro ao fazer login'}), 500

# ==================== PRÉ-MATRÍCULA ====================
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
    data_inscricao = dados.get('data_inscricao') or None
    data_entrega_uniforme = dados.get('data_entrega_uniforme') or None
    status = 'pendente'

    print(f"📥 Recebido: {nome_aluno}, Idade: {idade}, Tamanho: {tamanho_uniforme}")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as total FROM alunos 
            WHERE rg = %s AND responsavel = %s AND nome_aluno = %s
        """, (rg, responsavel, nome_aluno))
        
        resultado = cursor.fetchone()
        
        if resultado['total'] > 0:
            cursor.close()
            conn.close()
            return jsonify({'erro': 'Aluno já cadastrado'}), 409

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

# ==================== LISTAR ALUNOS ====================
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

# ==================== ATUALIZAR STATUS ====================
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

# ==================== EDITAR ALUNO ====================
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
            dados.get('data_entrega_uniforme') or None,
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

# ==================== ELOGIOS ====================
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

# ==================== STATUS (ONLINE/OFFLINE) ====================
@app.route('/api/status', methods=['GET', 'POST'])
def status():
    global sistema_status
    
    if request.method == 'GET':
        return jsonify({
            'online': sistema_status.get('online', True),
            'ultima_atualizacao': sistema_status.get('ultima_atualizacao', datetime.now().isoformat())
        }), 200
    
    elif request.method == 'POST':
        dados = request.json
        online = dados.get('online', True)
        sistema_status['online'] = online
        sistema_status['ultima_atualizacao'] = datetime.now().isoformat()
        print(f"📡 Status alterado para: {'ONLINE' if online else 'OFFLINE'}")
        return jsonify({
            'online': online,
            'mensagem': f"Status alterado para {'ONLINE' if online else 'OFFLINE'}"
        }), 200

# ==================== CONTATOS ====================
@app.route('/api/contatos', methods=['GET', 'POST'])
def contatos():
    if request.method == 'GET':
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, whatsapp, assunto, mensagem, data_envio as data
                FROM contatos 
                ORDER BY id DESC
            """)
            contatos = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify(contatos), 200
        except Exception as e:
            print(f"❌ Erro ao buscar contatos: {e}")
            return jsonify({'erro': 'Erro ao buscar contatos'}), 500
    
    elif request.method == 'POST':
        dados = request.json
        nome = dados.get('nome', '')
        whatsapp = dados.get('whatsapp', '')
        assunto = dados.get('assunto', '')
        mensagem = dados.get('mensagem', '')
        data_envio = datetime.now().isoformat()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contatos (nome, whatsapp, assunto, mensagem, data_envio)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (nome, whatsapp, assunto, mensagem, data_envio))
            novo_id = cursor.fetchone()['id']
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'mensagem': 'Contato salvo!', 'id': novo_id}), 201
        except Exception as e:
            print(f"❌ Erro ao salvar contato: {e}")
            return jsonify({'erro': str(e)}), 500

@app.route('/api/contatos/<int:id>', methods=['DELETE'])
def excluir_contato(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contatos WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'mensagem': 'Contato excluído!'}), 200
    except Exception as e:
        print(f"❌ Erro ao excluir contato: {e}")
        return jsonify({'erro': str(e)}), 500

# ==================== NOTÍCIAS ====================
@app.route('/api/noticias', methods=['GET'])
def get_noticias():
    """Busca todas as notícias ativas (não expiradas)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, texto, imagem_url, data_publicacao, data_expiracao, ativo
            FROM noticias 
            WHERE ativo = TRUE 
              AND (data_expiracao IS NULL OR data_expiracao > NOW())
            ORDER BY data_publicacao DESC
        """)
        noticias = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(noticias), 200
    except Exception as e:
        print(f"❌ Erro ao buscar notícias: {e}")
        return jsonify({'erro': 'Erro ao buscar notícias'}), 500

@app.route('/api/noticias/todas', methods=['GET'])
def get_todas_noticias():
    """Busca TODAS as notícias (para a diretoria)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, texto, imagem_url, data_publicacao, data_expiracao, ativo
            FROM noticias 
            ORDER BY data_publicacao DESC
        """)
        noticias = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(noticias), 200
    except Exception as e:
        print(f"❌ Erro ao buscar notícias: {e}")
        return jsonify({'erro': 'Erro ao buscar notícias'}), 500

@app.route('/api/noticias', methods=['POST'])
def publicar_noticia():
    """Publica uma nova notícia com upload de imagem para o Cloudinary"""
    dados = request.json
    
    titulo = dados.get('titulo', '').strip()
    texto = dados.get('texto', '').strip()
    imagem_base64 = dados.get('imagem_base64', '')
    dias_expiracao = int(dados.get('dias_expiracao', 30))
    
    if not titulo:
        return jsonify({'erro': 'Título é obrigatório'}), 400
    
    try:
        imagem_url = None
        
        # Upload da imagem para o Cloudinary
        if imagem_base64:
            try:
                upload_result = cloudinary.uploader.upload(
                 imagem_base64,
                 upload_preset='escolinha_jacare'
                )
                
                imagem_url = upload_result.get('secure_url')
                print(f"✅ Imagem enviada para Cloudinary: {imagem_url}")
            except Exception as e:
                print(f"⚠️ Erro ao enviar imagem: {e}")
                return jsonify({'erro': f'Erro ao enviar imagem: {str(e)}'}), 500
        
        # Calcula a data de expiração
        from datetime import timedelta
        data_expiracao = datetime.now() + timedelta(days=dias_expiracao)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO noticias (titulo, texto, imagem_url, data_expiracao, ativo)
            VALUES (%s, %s, %s, %s, TRUE)
            RETURNING id
        """, (titulo, texto, imagem_url, data_expiracao))
        novo_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Notícia publicada! ID: {novo_id}")
        return jsonify({
            'mensagem': 'Notícia publicada com sucesso!',
            'id': novo_id,
            'imagem_url': imagem_url
        }), 201
        
    except Exception as e:
        print(f"❌ Erro ao publicar notícia: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/noticias/<int:id>', methods=['DELETE'])
def excluir_noticia(id):
    """Exclui uma notícia e sua imagem do Cloudinary"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Primeiro, busca a URL da imagem
        cursor.execute("SELECT imagem_url FROM noticias WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        
        if resultado and resultado['imagem_url']:
            # Tenta extrair o public_id do Cloudinary da URL
            try:
                url = resultado['imagem_url']
                # Exemplo: https://res.cloudinary.com/PBMaz3jx/image/upload/v123456/noticias/abc123.jpg
                if 'cloudinary.com' in url:
                    partes = url.split('/upload/')
                    if len(partes) > 1:
                        caminho = partes[1]
                        # Remove a versão (v123456/)
                        if caminho.startswith('v'):
                            caminho = '/'.join(caminho.split('/')[1:])
                        # Remove a extensão
                        public_id = caminho.rsplit('.', 1)[0]
                        cloudinary.uploader.destroy(public_id)
                        print(f"🗑️ Imagem excluída do Cloudinary: {public_id}")
            except Exception as e:
                print(f"⚠️ Erro ao excluir imagem do Cloudinary: {e}")
        
        # Exclui do banco
        cursor.execute("DELETE FROM noticias WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'mensagem': 'Notícia excluída!'}), 200
    except Exception as e:
        print(f"❌ Erro ao excluir notícia: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/api/noticias/limpar-expiradas', methods=['POST'])
def limpar_noticias_expiradas():
    """Limpa notícias expiradas e suas imagens do Cloudinary"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Busca notícias expiradas
        cursor.execute("""
            SELECT id, imagem_url FROM noticias 
            WHERE ativo = TRUE 
              AND data_expiracao IS NOT NULL 
              AND data_expiracao <= NOW()
        """)
        expiradas = cursor.fetchall()
        
        # Exclui imagens do Cloudinary
        for noticia in expiradas:
            if noticia['imagem_url'] and 'cloudinary.com' in noticia['imagem_url']:
                try:
                    url = noticia['imagem_url']
                    partes = url.split('/upload/')
                    if len(partes) > 1:
                        caminho = partes[1]
                        if caminho.startswith('v'):
                            caminho = '/'.join(caminho.split('/')[1:])
                        public_id = caminho.rsplit('.', 1)[0]
                        cloudinary.uploader.destroy(public_id)
                except Exception as e:
                    print(f"⚠️ Erro ao excluir imagem: {e}")
        
        # Marca como inativas (ou exclui de vez)
        cursor.execute("""
            UPDATE noticias SET ativo = FALSE 
            WHERE ativo = TRUE 
              AND data_expiracao IS NOT NULL 
              AND data_expiracao <= NOW()
        """)
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensagem': f'{len(expiradas)} notícias expiradas foram limpas!',
            'total': len(expiradas)
        }), 200
    except Exception as e:
        print(f"❌ Erro ao limpar notícias: {e}")
        return jsonify({'erro': str(e)}), 500

# ==================== NOTIFICAÇÕES ====================
@app.route('/api/notificacoes', methods=['GET'])
def get_notificacoes():
    """Retorna contadores e listas de notificações para o sino"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Matrículas pendentes (total)
        cursor.execute("SELECT COUNT(*) as total FROM alunos WHERE status = 'pendente'")
        matriculas = cursor.fetchone()['total']
        
        # 2. Contatos dos últimos 7 dias
        cursor.execute("""
            SELECT COUNT(*) as total FROM contatos 
            WHERE data_envio > NOW() - INTERVAL '7 days'
        """)
        contatos = cursor.fetchone()['total']
        
        # 3. Notícias ativas dos últimos 7 dias
        cursor.execute("""
            SELECT COUNT(*) as total FROM noticias 
            WHERE ativo = TRUE 
              AND data_publicacao > NOW() - INTERVAL '7 days'
              AND (data_expiracao IS NULL OR data_expiracao > NOW())
        """)
        noticias = cursor.fetchone()['total']
        
        # Últimas 5 matrículas pendentes
        cursor.execute("""
            SELECT protocolo, nome_aluno, turma, data_envio 
            FROM alunos 
            WHERE status = 'pendente' 
            ORDER BY id DESC 
            LIMIT 5
        """)
        ultimas_matriculas = cursor.fetchall()
        
        # Últimos 5 contatos
        cursor.execute("""
            SELECT id, nome, assunto, mensagem, data_envio 
            FROM contatos 
            ORDER BY id DESC 
            LIMIT 5
        """)
        ultimos_contatos = cursor.fetchall()
        
        # Últimas 5 notícias ativas
        cursor.execute("""
            SELECT id, titulo, data_publicacao 
            FROM noticias 
            WHERE ativo = TRUE 
              AND (data_expiracao IS NULL OR data_expiracao > NOW())
            ORDER BY data_publicacao DESC 
            LIMIT 5
        """)
        ultimas_noticias = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        total = matriculas + contatos + noticias
        
        print(f"🔔 Notificações: {total} total (M:{matriculas} C:{contatos} N:{noticias})")
        
        return jsonify({
            'total': total,
            'matriculas': matriculas,
            'contatos': contatos,
            'noticias': noticias,
            'ultimas_matriculas': ultimas_matriculas,
            'ultimos_contatos': ultimos_contatos,
            'ultimas_noticias': ultimas_noticias
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao buscar notificações: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
