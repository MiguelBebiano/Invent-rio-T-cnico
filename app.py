# # pip install pandas openpyxl pillow


# from flask import Flask, render_template, request, jsonify, send_file
# import pymysql
# import os
# import pandas as pd
# from PIL import Image # Para análise de imagem
# from io import BytesIO # Para trabalhar com arquivos em memória
# from google import genai
# from google.genai.errors import APIError

# # =========================================================
# # ⚠️ IMPORTANTE: INSERIR A CHAVE DE API AQUI (APENAS PARA TESTES LOCAIS)
# # =========================================================
# GEMINI_API_KEY = "AIzaSyAOYKWb1cQsGg1dlPjcIUADiwpkAEPdAwE"
# UPLOAD_FOLDER = 'uploads' # Pasta para salvar imagens temporárias
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
# # =========================================================

# # --- Configuração Principal da Aplicação ---
# app = Flask(__name__) # APENAS UMA VEZ!
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def get_db_connection(): # APENAS UMA VEZ!
#     return pymysql.connect(
#         host='localhost',
#         user='root',
#         password='Math8080@',
#         database='sistema_hardware',
#         cursorclass=pymysql.cursors.DictCursor
#     )

# # --- Configuração da API do Gemini ---
# try:
#     client = genai.Client(api_key=GEMINI_API_KEY)
#     print("Cliente Gemini inicializado com sucesso.")
# except Exception as e:
#     print(f"Erro ao inicializar o cliente Gemini. Erro: {e}")
#     client = None

# # --- Rotas ---

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/buscar', methods=['POST'])
# def buscar():
#     nome_item = request.json.get('nome')
#     itens_encontrados = []
    
#     # 1. Busca no MySQL (Continua o mesmo)
#     # ... (código de busca no MySQL) ...
    
#     # 2. Chamada Real para o Gemini API (Aprimorada)
#     sugestao_ia = "Não foi possível obter sugestões da IA."
    
#     if client:
#         prompt_info = (
#             f"Você é um especialista em hardware e redes. Forneça uma breve descrição (valor aproximado e função) e 3 sugestões de itens relacionados "
#             f"ao termo de busca '{nome_item}'. Responda em formato de lista e de forma concisa em português. "
#             f"Se o item já existe no banco ({itens_encontrados}), use os dados para complementar, caso contrário, use seu conhecimento geral."
#         )

#         try:
#             response = client.models.generate_content(
#                 model='gemini-2.5-flash',
#                 contents=prompt_info
#             )
#             sugestao_ia = response.text
#         except APIError as e:
#             sugestao_ia = f"Erro ao acessar a API do Gemini: {e.message}."
#         except Exception as e:
#             sugestao_ia = f"Erro desconhecido na IA: {e}"
    
#     # Retorna os dados do banco, a sugestão da IA e o nome do item para o front-end salvar
#     return jsonify({
#         "itens": itens_encontrados,
#         "sugestao_ia": sugestao_ia,
#         "item_para_salvar": nome_item # Enviamos o nome de volta para o JavaScript usar no botão Salvar
#     })

# @app.route('/salvar_item', methods=['POST'])
# def salvar_item():
#     data = request.json
#     nome = data.get('nome')
#     valor_str = data.get('valor', '0.00').replace(',', '.') # Substitui vírgula por ponto
#     descricao = data.get('descricao', '')
#     categoria = data.get('categoria', 'Não Classificado')
    
#     try:
#         valor = float(valor_str)
#     except ValueError:
#         valor = 0.00
        
#     try:
#         conn = get_db_connection()
#         with conn.cursor() as cursor:
#             sql = "INSERT INTO itens (nome, categoria, valor, descricao) VALUES (%s, %s, %s, %s)"
#             cursor.execute(sql, (nome, categoria, valor, descricao))
#         conn.commit()
#         conn.close()
#         return jsonify({"success": True, "message": f"Item '{nome}' salvo com sucesso!"})
#     except Exception as e:
#         return jsonify({"success": False, "message": f"Erro ao salvar: {e}"}), 500

# @app.route('/exportar_excel', methods=['GET'])
# def exportar_excel():
#     try:
#         conn = get_db_connection()
#         # Executa a query e lê diretamente para um DataFrame do Pandas
#         df = pd.read_sql('SELECT nome, categoria, valor, descricao FROM itens', conn)
#         conn.close()

#         # Salva o DataFrame em um buffer de memória
#         output = BytesIO()
#         writer = pd.ExcelWriter(output, engine='openpyxl')
#         df.to_excel(writer, index=False, sheet_name='Inventário')
#         writer.close()
#         output.seek(0)
        
#         # Envia o arquivo para download
#         return send_file(
#             output,
#             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#             download_name='inventario_hardware.xlsx',
#             as_attachment=True
#         )

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/chat_tecnico', methods=['POST'])
# def chat_tecnico():
#     pergunta = request.json.get('pergunta')
    
#     # 1. Recuperar itens do banco para contextualização
#     itens_banco = []
#     try:
#         conn = get_db_connection()
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT nome, categoria FROM itens LIMIT 10") # Pega os últimos 10 itens
#             itens_banco = cursor.fetchall()
#         conn.close()
#     except Exception as e:
#         print(f"Erro ao buscar itens para chat: {e}")

#     # 2. Construir o Prompt
#     contexto = f"Itens no seu inventário para referência: {itens_banco}"
    
#     prompt = (
#         f"Você é um chatbot de suporte técnico focado em hardware e redes. "
#         f"Com base no seu inventário ({contexto}), responda a seguinte pergunta: '{pergunta}'. "
#         f"Se for relevante, pergunte se o usuário tem dúvidas sobre algum dos itens em estoque."
#     )
    
#     # 3. Chamar o Gemini
#     if client:
#         try:
#             response = client.models.generate_content(
#                 model='gemini-2.5-flash',
#                 contents=prompt
#             )
#             return jsonify({"resposta": response.text})
#         except Exception as e:
#             return jsonify({"resposta": f"Desculpe, a IA está indisponível. Erro: {e}"}), 500
            
#     return jsonify({"resposta": "Serviço de IA não configurado."})

# @app.route('/analisar_imagem', methods=['POST'])
# def analisar_imagem():
#     if 'foto' not in request.files:
#         return jsonify({"error": "Nenhuma imagem enviada."}), 400

#     foto = request.files['foto']
#     descricao_problema = request.form.get('descricao_problema', 'Nenhuma descrição fornecida.')

#     if foto.filename == '':
#         return jsonify({"error": "Nome de arquivo inválido."}), 400

#     if foto and client:
#         try:
#             # 1. Carrega a imagem na memória
#             img_bytes = foto.read()
#             image = Image.open(BytesIO(img_bytes))
            
#             # 2. Cria o Prompt Multimodal
#             prompt = (
#                 f"Análise de Hardware/Redes. O usuário enviou a imagem com a seguinte descrição do problema: '{descricao_problema}'. "
#                 f"Analise a imagem e a descrição. Identifique o item, descreva o problema aparente (se houver) e forneça um nível de ajuda/diagnóstico (Ex: Baixo, Médio, Alto). "
#                 f"Dê sugestões de solução ou próximos passos. Responda em português."
#             )

#             # 3. Chama o Gemini com Imagem e Texto
#             response = client.models.generate_content(
#                 model='gemini-2.5-flash', # ou gemini-2.5-pro
#                 contents=[image, prompt]
#             )
            
#             return jsonify({"analise": response.text})
            
#         except Exception as e:
#             print(f"Erro na análise de imagem: {e}")
#             return jsonify({"analise": f"Erro no processamento da imagem ou IA: {e}"}), 500

#     return jsonify({"analise": "Serviço de IA ou imagem não configurados."})



# if __name__ == '__main__':
#     app.run(debug=True)





from flask import Flask, render_template, request, jsonify, send_file
import pymysql
import os
import pandas as pd
from PIL import Image
from io import BytesIO
from google import genai
from google.genai.errors import APIError

# =========================================================
# ⚠️ 1. CONFIGURAÇÕES DE SEGURANÇA E AMBIENTE ⚠️
# Use .env em produção!
# =========================================================
# Sua chave de API do Gemini (Para testes)
GEMINI_API_KEY = "AIzaSyAOYKWb1cQsGg1dlPjcIUADiwpkAEPdAwE"

# Configuração da pasta para upload temporário de imagens
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================================================
# 2. CONEXÃO COM BANCO DE DADOS
# =========================================================
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='etecembu@123',
        database='sistema_hardware',
        cursorclass=pymysql.cursors.DictCursor
    )

# =========================================================
# 3. INICIALIZAÇÃO DO CLIENTE GEMINI
# =========================================================
try:
    # Passamos a chave diretamente para o construtor 'Client'
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("Cliente Gemini inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o cliente Gemini. Erro: {e}")
    client = None

# =========================================================
# 4. ROTAS DA APLICAÇÃO
# =========================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    nome_item = request.json.get('nome')
    itens_encontrados = []
    sugestao_ia = "Não foi possível obter sugestões da IA."
    
    # 1. Busca no MySQL
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM itens WHERE nome LIKE %s"
            cursor.execute(sql, ('%' + nome_item + '%',))
            itens_encontrados = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erro no MySQL: {e}")

    # 2. Chamada Real para o Gemini API (Com estrutura Markdown)
    if client:
        # Cria o prompt com a estrutura Markdown exigida para melhor leitura
        prompt_info = (
            f"Você é um especialista em hardware e redes, fornecendo diagnósticos e informações concisas. "
            f"O usuário buscou o item '{nome_item}'. "
            f"Sua resposta DEVE ser formatada usando Markdown para fácil leitura e deve seguir esta estrutura: "
            f"\n\n## 💡 Informações Principais sobre '{nome_item}'"
            f"\n* **Função/Descrição:** Breve explicação de sua utilidade."
            f"\n* **Valor Médio Aproximado:** (Ex: R$ 1.500,00)"
            f"\n\n## 🔗 Sugestões Relacionadas"
            f"\nListe 3 componentes compatíveis ou semelhantes que um técnico deveria considerar."
            f"\n\nResponda diretamente com esta estrutura, sem introduções desnecessárias."
        )

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_info
            )
            sugestao_ia = response.text
        except APIError as e:
            sugestao_ia = f"Erro ao acessar a API do Gemini: {e.message}."
        except Exception as e:
            sugestao_ia = f"Erro desconhecido na IA: {e}"
    
    return jsonify({
        "itens": itens_encontrados,
        "sugestao_ia": sugestao_ia,
        "item_para_salvar": nome_item
    })

@app.route('/salvar_item', methods=['POST'])
def salvar_item():
    data = request.json
    nome = data.get('nome')
    valor_str = data.get('valor', '0.00').replace(',', '.')
    descricao = data.get('descricao', '')
    categoria = data.get('categoria', 'Não Classificado')
    
    try:
        valor = float(valor_str)
    except ValueError:
        valor = 0.00
        
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO itens (nome, categoria, valor, descricao) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nome, categoria, valor, descricao))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Item '{nome}' salvo com sucesso!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao salvar: {e}"}), 500

@app.route('/exportar_excel', methods=['GET'])
def exportar_excel():
    try:
        conn = get_db_connection()
        df = pd.read_sql('SELECT nome, categoria, valor, descricao FROM itens', conn)
        conn.close()

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Inventário')
        writer.close()
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='inventario_hardware.xlsx',
            as_attachment=True
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat_tecnico', methods=['POST'])
def chat_tecnico():
    pergunta = request.json.get('pergunta')
    
    itens_banco = []
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT nome, categoria FROM itens LIMIT 10")
            itens_banco = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar itens para chat: {e}")

    contexto = f"Itens no seu inventário para referência: {itens_banco}"
    
    prompt = (
        f"Você é um chatbot de suporte técnico focado em hardware e redes, com foco em ser conciso e útil. "
        f"Com base no seu inventário ({contexto}), responda a seguinte pergunta: '{pergunta}'. "
        f"Use formatação Markdown simples (negrito, listas) para melhor leitura."
    )
    
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return jsonify({"resposta": response.text})
        except Exception as e:
            return jsonify({"resposta": f"Desculpe, a IA está indisponível. Erro: {e}"}), 500
            
    return jsonify({"resposta": "Serviço de IA não configurado."})

@app.route('/analisar_imagem', methods=['POST'])
def analisar_imagem():
    if 'foto' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada."}), 400

    foto = request.files['foto']
    descricao_problema = request.form.get('descricao_problema', 'Nenhuma descrição fornecida.')

    if foto.filename == '':
        return jsonify({"error": "Nome de arquivo inválido."}), 400

    if foto and client:
        try:
            # Carrega a imagem na memória
            img_bytes = foto.read()
            image = Image.open(BytesIO(img_bytes))
            
            # Cria o Prompt Multimodal
            prompt = (
                f"Análise de Hardware/Redes. O usuário enviou a imagem com a seguinte descrição do problema: '{descricao_problema}'. "
                f"Analise a imagem e a descrição. **Identifique o item, descreva o problema aparente e forneça um NÍVEL DE URGÊNCIA (Baixo/Médio/Alto).** "
                f"Dê sugestões de solução ou próximos passos. Responda em Português usando Markdown para formatação clara."
            )

            # Chama o Gemini com Imagem e Texto
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[image, prompt]
            )
            
            return jsonify({"analise": response.text})
            
        except Exception as e:
            print(f"Erro na análise de imagem: {e}")
            return jsonify({"analise": f"Erro no processamento da imagem ou IA: {e}"}), 500

    return jsonify({"analise": "Serviço de IA ou imagem não configurados."})

if __name__ == '__main__':
    app.run(debug=True)   