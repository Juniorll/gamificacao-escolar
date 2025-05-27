"""
Módulo de rotas para administração do sistema.
Este arquivo contém as rotas para configurações e personalizações do sistema.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from src.models.database import db, Configuracao
import os
import json
from werkzeug.utils import secure_filename

# Criação do blueprint de administração
admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/configuracoes", methods=["GET"])
@login_required
def listar_configuracoes():
    """
    Lista todas as configurações do sistema.
    """
    configuracoes = Configuracao.query.all()
    resultado = {}
    
    for config in configuracoes:
        try:
            valor = json.loads(config.valor)
        except:
            valor = config.valor
        
        resultado[config.chave] = {
            "valor": valor,
            "descricao": config.descricao
        }
    
    return jsonify(resultado), 200

@admin_bp.route("/configuracoes/<string:chave>", methods=["GET"])
def obter_configuracao(chave):
    """
    Obtém uma configuração específica pelo nome da chave.
    """
    configuracao = Configuracao.query.filter_by(chave=chave).first()
    
    if not configuracao:
        return jsonify({"mensagem": "Configuração não encontrada"}), 404
    
    try:
        valor = json.loads(configuracao.valor)
    except:
        valor = configuracao.valor
    
    return jsonify({
        "chave": configuracao.chave,
        "valor": valor,
        "descricao": configuracao.descricao
    }), 200

@admin_bp.route("/configuracoes", methods=["POST"])
@login_required
def criar_configuracao():
    """
    Cria ou atualiza uma configuração do sistema.
    """
    data = request.get_json()
    
    if not data or not data.get("chave") or "valor" not in data:
        return jsonify({"mensagem": "Chave e valor são obrigatórios"}), 400
    
    chave = data["chave"]
    valor = data["valor"]
    descricao = data.get("descricao", "")
    
    # Converter valor para JSON se for um objeto
    if isinstance(valor, (dict, list)):
        valor = json.dumps(valor)
    else:
        valor = str(valor)
    
    # Verificar se a configuração já existe
    configuracao = Configuracao.query.filter_by(chave=chave).first()
    
    if configuracao:
        configuracao.valor = valor
        configuracao.descricao = descricao
    else:
        configuracao = Configuracao(chave=chave, valor=valor, descricao=descricao)
        db.session.add(configuracao)
    
    db.session.commit()
    
    return jsonify({
        "mensagem": "Configuração salva com sucesso",
        "configuracao": {
            "chave": chave,
            "valor": data["valor"],  # Retorna o valor original, não o JSON
            "descricao": descricao
        }
    }), 200

@admin_bp.route("/upload/imagem", methods=["POST"])
@login_required
def upload_imagem():
    """
    Faz upload de uma imagem para o sistema.
    """
    if "arquivo" not in request.files:
        return jsonify({"mensagem": "Nenhum arquivo enviado"}), 400
    
    arquivo = request.files["arquivo"]
    tipo = request.form.get("tipo", "geral")  # geral, avatar, logo, icone, gif
    
    if arquivo.filename == "":
        return jsonify({"mensagem": "Nenhum arquivo selecionado"}), 400
    
    # Verificar extensão do arquivo
    extensoes_permitidas = {"png", "jpg", "jpeg", "gif", "webp"}
    if "." not in arquivo.filename or arquivo.filename.rsplit(".", 1)[1].lower() not in extensoes_permitidas:
        return jsonify({"mensagem": "Formato de arquivo não permitido"}), 400
    
    # Criar diretório se não existir
    diretorio = os.path.join(current_app.static_folder, "uploads", tipo)
    os.makedirs(diretorio, exist_ok=True)
    
    # Salvar arquivo
    nome_arquivo = secure_filename(arquivo.filename)
    caminho_arquivo = os.path.join(diretorio, nome_arquivo)
    arquivo.save(caminho_arquivo)
    
    # Caminho relativo para acesso via URL
    caminho_relativo = f"/static/uploads/{tipo}/{nome_arquivo}"
    
    return jsonify({
        "mensagem": "Arquivo enviado com sucesso",
        "arquivo": {
            "nome": nome_arquivo,
            "caminho": caminho_relativo,
            "tipo": tipo
        }
    }), 201

@admin_bp.route("/imagens/<string:tipo>", methods=["GET"])
def listar_imagens(tipo):
    """
    Lista todas as imagens de um tipo específico.
    """
    # Verificar se o tipo é válido
    tipos_validos = {"geral", "avatar", "logo", "icone", "gif"}
    if tipo not in tipos_validos:
        return jsonify({"mensagem": "Tipo de imagem inválido"}), 400
    
    # Caminho do diretório
    diretorio = os.path.join(current_app.static_folder, "uploads", tipo)
    
    # Verificar se o diretório existe
    if not os.path.exists(diretorio):
        return jsonify({"imagens": []}), 200
    
    # Listar arquivos
    arquivos = os.listdir(diretorio)
    extensoes_permitidas = {"png", "jpg", "jpeg", "gif", "webp"}
    imagens = []
    
    for arquivo in arquivos:
        if "." in arquivo and arquivo.rsplit(".", 1)[1].lower() in extensoes_permitidas:
            caminho_relativo = f"/static/uploads/{tipo}/{arquivo}"
            imagens.append({
                "nome": arquivo,
                "caminho": caminho_relativo,
                "tipo": tipo
            })
    
    return jsonify({"imagens": imagens}), 200

@admin_bp.route("/importar/alunos", methods=["POST"])
@login_required
def importar_alunos():
    """
    Importa alunos a partir de um arquivo CSV ou JSON.
    """
    if "arquivo" not in request.files:
        return jsonify({"mensagem": "Nenhum arquivo enviado"}), 400
    
    arquivo = request.files["arquivo"]
    turma_id = request.form.get("turma_id")
    
    if not turma_id:
        return jsonify({"mensagem": "ID da turma é obrigatório"}), 400
    
    # Verificar se a turma existe e pertence ao professor
    turma = Turma.query.filter_by(id=turma_id, professor_id=current_user.id).first()
    if not turma:
        return jsonify({"mensagem": "Turma inválida ou não pertence ao professor"}), 403
    
    if arquivo.filename == "":
        return jsonify({"mensagem": "Nenhum arquivo selecionado"}), 400
    
    # Verificar extensão do arquivo
    if "." not in arquivo.filename:
        return jsonify({"mensagem": "Formato de arquivo inválido"}), 400
    
    extensao = arquivo.filename.rsplit(".", 1)[1].lower()
    
    alunos_importados = []
    erros = []
    
    try:
        if extensao == "csv":
            # Processar CSV
            import csv
            import io
            
            stream = io.StringIO(arquivo.stream.read().decode("utf-8"))
            reader = csv.DictReader(stream)
            
            for row in reader:
                try:
                    nome = row.get("nome")
                    email = row.get("email")
                    
                    if not nome:
                        erros.append(f"Linha sem nome: {row}")
                        continue
                    
                    # Verificar se o aluno já existe
                    aluno_existente = Aluno.query.filter_by(email=email).first() if email else None
                    
                    if aluno_existente:
                        erros.append(f"Aluno com email {email} já existe")
                        continue
                    
                    novo_aluno = Aluno(
                        nome=nome,
                        email=email,
                        turma_id=turma_id
                    )
                    db.session.add(novo_aluno)
                    alunos_importados.append({"nome": nome, "email": email})
                except Exception as e:
                    erros.append(f"Erro ao processar linha: {str(e)}")
        
        elif extensao == "json":
            # Processar JSON
            import json
            
            dados = json.loads(arquivo.read())
            
            if not isinstance(dados, list):
                return jsonify({"mensagem": "Formato JSON inválido. Deve ser uma lista de alunos"}), 400
            
            for item in dados:
                try:
                    nome = item.get("nome")
                    email = item.get("email")
                    
                    if not nome:
                        erros.append(f"Item sem nome: {item}")
                        continue
                    
                    # Verificar se o aluno já existe
                    aluno_existente = Aluno.query.filter_by(email=email).first() if email else None
                    
                    if aluno_existente:
                        erros.append(f"Aluno com email {email} já existe")
                        continue
                    
                    novo_aluno = Aluno(
                        nome=nome,
                        email=email,
                        turma_id=turma_id
                    )
                    db.session.add(novo_aluno)
                    alunos_importados.append({"nome": nome, "email": email})
                except Exception as e:
                    erros.append(f"Erro ao processar item: {str(e)}")
        
        else:
            return jsonify({"mensagem": "Formato de arquivo não suportado. Use CSV ou JSON"}), 400
        
        # Salvar alterações no banco de dados
        db.session.commit()
        
        return jsonify({
            "mensagem": f"{len(alunos_importados)} alunos importados com sucesso",
            "alunos_importados": alunos_importados,
            "erros": erros
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": f"Erro ao importar alunos: {str(e)}"}), 500
