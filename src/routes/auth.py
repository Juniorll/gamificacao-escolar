"""
Módulo de autenticação para o sistema de gamificação escolar.
Este arquivo contém as rotas e funções relacionadas à autenticação de professores.
"""

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.database import db, Professor
import re

# Criação do blueprint de autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Rota para autenticação de professores.
    
    Recebe email e senha via JSON e autentica o professor.
    Retorna token de autenticação em caso de sucesso.
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha'):
        return jsonify({'mensagem': 'Dados incompletos'}), 400
    
    email = data.get('email')
    senha = data.get('senha')
    
    # Busca o professor pelo email
    professor = Professor.query.filter_by(email=email).first()
    
    # Verifica se o professor existe e se a senha está correta
    if not professor or not check_password_hash(professor.senha_hash, senha):
        return jsonify({'mensagem': 'Email ou senha incorretos'}), 401
    
    # Verifica se o professor está ativo
    if not professor.ativo:
        return jsonify({'mensagem': 'Conta desativada. Entre em contato com o administrador.'}), 403
    
    # Realiza o login do professor
    login_user(professor)
    
    # Retorna os dados do professor logado
    return jsonify({
        'mensagem': 'Login realizado com sucesso',
        'professor': {
            'id': professor.id,
            'nome': professor.nome,
            'email': professor.email
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Rota para logout de professores.
    
    Encerra a sessão do professor autenticado.
    """
    logout_user()
    return jsonify({'mensagem': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    """
    Rota para cadastro de novos professores.
    
    Recebe dados do professor via JSON e cria um novo registro.
    """
    data = request.get_json()
    
    # Verifica se todos os campos obrigatórios foram enviados
    if not data or not data.get('nome') or not data.get('email') or not data.get('senha'):
        return jsonify({'mensagem': 'Dados incompletos'}), 400
    
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    
    # Validação do email
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'mensagem': 'Email inválido'}), 400
    
    # Validação da senha (mínimo 6 caracteres)
    if len(senha) < 6:
        return jsonify({'mensagem': 'A senha deve ter pelo menos 6 caracteres'}), 400
    
    # Verifica se o email já está em uso
    if Professor.query.filter_by(email=email).first():
        return jsonify({'mensagem': 'Email já cadastrado'}), 400
    
    # Cria um novo professor
    novo_professor = Professor(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha)
    )
    
    # Adiciona o professor ao banco de dados
    db.session.add(novo_professor)
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Professor cadastrado com sucesso',
        'professor': {
            'id': novo_professor.id,
            'nome': novo_professor.nome,
            'email': novo_professor.email
        }
    }), 201

@auth_bp.route('/perfil', methods=['GET'])
@login_required
def perfil():
    """
    Rota para obter os dados do professor autenticado.
    """
    return jsonify({
        'professor': {
            'id': current_user.id,
            'nome': current_user.nome,
            'email': current_user.email
        }
    }), 200

@auth_bp.route('/perfil', methods=['PUT'])
@login_required
def atualizar_perfil():
    """
    Rota para atualizar os dados do professor autenticado.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'mensagem': 'Dados incompletos'}), 400
    
    # Atualiza os campos enviados
    if 'nome' in data:
        current_user.nome = data['nome']
    
    if 'email' in data:
        # Validação do email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return jsonify({'mensagem': 'Email inválido'}), 400
        
        # Verifica se o email já está em uso por outro professor
        professor_existente = Professor.query.filter_by(email=data['email']).first()
        if professor_existente and professor_existente.id != current_user.id:
            return jsonify({'mensagem': 'Email já cadastrado'}), 400
        
        current_user.email = data['email']
    
    if 'senha' in data:
        # Validação da senha (mínimo 6 caracteres)
        if len(data['senha']) < 6:
            return jsonify({'mensagem': 'A senha deve ter pelo menos 6 caracteres'}), 400
        
        current_user.senha_hash = generate_password_hash(data['senha'])
    
    # Salva as alterações
    db.session.commit()
    
    return jsonify({
        'mensagem': 'Perfil atualizado com sucesso',
        'professor': {
            'id': current_user.id,
            'nome': current_user.nome,
            'email': current_user.email
        }
    }), 200

# Função para carregar o usuário pelo ID (necessário para o Flask-Login)
@current_app.login_manager.user_loader
def load_user(user_id):
    """
    Função para carregar o usuário pelo ID.
    Necessária para o funcionamento do Flask-Login.
    """
    return Professor.query.get(int(user_id))
