from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.database import db, Professor

# Cria o blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('professor.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        professor = Professor.query.filter_by(email=email).first()
        
        if professor and check_password_hash(professor.senha_hash, senha):
            login_user(professor)
            return redirect(url_for('professor.dashboard'))
        else:
            flash('Email ou senha incorretos. Tente novamente.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('professor.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        professor_existente = Professor.query.filter_by(email=email).first()
        
        if professor_existente:
            flash('Email já cadastrado. Tente outro email.', 'danger')
            return redirect(url_for('auth.cadastro'))
        
        novo_professor = Professor(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha)
        )
        
        db.session.add(novo_professor)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('cadastro.html')
